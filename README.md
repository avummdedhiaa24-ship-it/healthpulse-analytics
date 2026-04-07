# HealthPulse Analytics 🏥

Clinical data pipeline with ML monitoring, drift detection, and NLP text analysis for healthcare analytics.

## Features
- **FastAPI** backend with RESTful endpoints
- **NLP Pipeline** — entity extraction (spaCy) + text similarity (TF-IDF/cosine)
- **ML Monitoring** — model run tracking + drift detection
- **Streamlit** dashboard
- **Docker** containerized deployment

## NLP Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/nlp/entities` | POST | Extract names, dates, medical terms from text |
| `/nlp/similarity` | POST | Compare similarity between two patient notes |

## Tech Stack
Python · FastAPI · spaCy · scikit-learn · SQLAlchemy · Docker · Streamlit

## Run Locally
```bash
docker-compose up
```
Visit http://localhost:8000/docs for API documentation.
