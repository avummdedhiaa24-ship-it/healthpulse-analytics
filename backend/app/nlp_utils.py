import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str) -> list:
    """Extract named entities (names, dates, etc.) from text."""
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities


def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two patient notes."""
    docs = [text1, text2]
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs)
    similarity = cosine_similarity(tfidf[0], tfidf[1])
    return float(similarity[0][0])
