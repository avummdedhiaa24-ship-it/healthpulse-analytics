import io
import logging

import pandas as pd
from fastapi import UploadFile, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.patient import Patient

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"patient_id", "age", "gender", "bmi", "condition"}


def _validate_columns(df: pd.DataFrame) -> None:
    """Raise HTTPException if any required columns are missing."""
    missing = REQUIRED_COLUMNS - set(df.columns.str.strip().str.lower())
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {sorted(missing)}",
        )


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and drop rows that are entirely empty."""
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(how="all")
    return df


def _coerce_row(row: pd.Series) -> Patient | None:
    """
    Convert a DataFrame row to a Patient ORM object.
    Returns None and logs a warning if the row cannot be coerced.
    """
    try:
        return Patient(
            patient_id=str(row["patient_id"]).strip(),
            age=int(row["age"]),
            gender=str(row["gender"]).strip(),
            bmi=float(row["bmi"]),
            condition=str(row["condition"]).strip(),
        )
    except (ValueError, KeyError) as exc:
        logger.warning("Skipping malformed row (patient_id=%s): %s",
                       row.get("patient_id"), exc)
        return None


async def process_patient_csv(file: UploadFile, db: Session) -> dict:
    """
    Read an uploaded CSV, validate its schema, bulk-insert Patient records,
    and return a summary of the operation.

    Args:
        file: The multipart-uploaded CSV file.
        db:   An active SQLAlchemy session (injected via Depends).

    Returns:
        {
            "inserted": <int>,   # rows successfully inserted
            "skipped":  <int>,   # rows skipped due to bad data or duplicates
            "total":    <int>,   # total rows in the CSV (excluding header)
        }

    Raises:
        HTTPException 400: file is not readable as CSV or is empty.
        HTTPException 422: required columns are absent.
        HTTPException 500: unexpected database error.
    """
    # ── 1. Read the raw bytes and parse into a DataFrame ──────────────────
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        logger.error("Failed to parse uploaded file: %s", exc)
        raise HTTPException(
            status_code=400, detail="Could not parse file as CSV.") from exc

    if df.empty:
        raise HTTPException(
            status_code=400, detail="Uploaded CSV file is empty.")

    # ── 2. Validate & clean ────────────────────────────────────────────────
    _validate_columns(df)
    df = _clean_dataframe(df)
    total_rows = len(df)

    # ── 3. Coerce rows → ORM objects, collecting failures ─────────────────
    patients: list[Patient] = []
    skipped = 0

    for _, row in df.iterrows():
        patient = _coerce_row(row)
        if patient is None:
            skipped += 1
        else:
            patients.append(patient)

    if not patients:
        raise HTTPException(
            status_code=422,
            detail="No valid rows found in the uploaded CSV.",
        )

    # ── 4. Bulk insert with duplicate handling ─────────────────────────────
    try:
        db.bulk_save_objects(patients)
        db.commit()
        inserted = len(patients)
        logger.info("CSV upload: inserted=%d skipped=%d total=%d",
                    inserted, skipped, total_rows)

    except IntegrityError as exc:
        db.rollback()
        logger.warning(
            "Bulk insert hit duplicate patient_id(s), retrying row-by-row: %s", exc)
        inserted, skipped = _insert_row_by_row(patients, db, skipped)

    except Exception as exc:
        db.rollback()
        logger.error("Unexpected DB error during CSV insert: %s", exc)
        raise HTTPException(
            status_code=500, detail="Database error during insert.") from exc

    return {
        "inserted": inserted,
        "skipped": skipped,
        "total": total_rows,
    }


def _insert_row_by_row(patients: list[Patient], db: Session, initial_skipped: int) -> tuple[int, int]:
    """
    Fallback: insert patients one-by-one so duplicates are skipped
    individually rather than aborting the entire batch.
    """
    inserted = 0
    skipped = initial_skipped

    for patient in patients:
        try:
            db.add(patient)
            db.commit()
            inserted += 1
        except IntegrityError:
            db.rollback()
            logger.warning(
                "Duplicate patient_id='%s' — skipped.", patient.patient_id)
            skipped += 1
        except Exception as exc:
            db.rollback()
            logger.error(
                "Unexpected error inserting patient_id='%s': %s", patient.patient_id, exc)
            skipped += 1

    return inserted, skipped
