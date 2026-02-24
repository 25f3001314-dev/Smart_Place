"""
ml_model.py  —  SmartMatchEngine: Pure-Python TF-IDF with N-grams & Cosine Similarity
---------------------------------------------------------------------------------------
No numpy / sklearn required — works on Python 3.14+ without C-extension DLLs.
Handles bigrams like "machine learning", "data science", "deep learning" properly.

API mirrors the sklearn SmartMatchEngine interface requested:
    engine = SmartMatchEngine()
    score  = engine.get_fit_score(student_profile, job_description)  → float 0-100
    scores = ml_fit_score(student_profile, [job1, job2, ...])         → list[int]
"""

import math
import re
from collections import Counter


# ── Text helpers ─────────────────────────────────────────────────────────────

# Common English stop words (subset — enough for resume/JD matching)
_STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "this","that","these","those","it","its","we","our","you","your","they",
    "their","i","my","me","him","her","us","who","which","what","how","when",
    "where","as","if","than","then","so","not","no","can","need","also",
    "required","must","good","strong","experience","knowledge","ability",
    "excellent","looking","seeking","candidate","position","role","team",
    "work","working","job","responsibilities","skills","using","use",
}


def _tokenize(text: str) -> list[str]:
    """Lowercase and extract alphanumeric tokens, filtering stop words."""
    raw = re.findall(r"[a-z][a-z0-9]*", text.lower())
    return [t for t in raw if t not in _STOP_WORDS and len(t) > 1]


def _ngrams(tokens: list[str], n: int) -> list[str]:
    """Generate n-grams joined by underscore."""
    return ["_".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def _build_terms(text: str, ngram_range: tuple[int, int] = (1, 2)) -> list[str]:
    """Tokenise + generate all n-grams in the given range."""
    tokens = _tokenize(text)
    terms  = []
    for n in range(ngram_range[0], ngram_range[1] + 1):
        terms.extend(_ngrams(tokens, n))
    return terms


def _tf(terms: list[str]) -> dict[str, float]:
    """Term frequency normalised by document length."""
    counts = Counter(terms)
    total  = len(terms) or 1
    return {term: count / total for term, count in counts.items()}


def _idf(corpus_terms: list[list[str]]) -> dict[str, float]:
    """Smoothed IDF over corpus."""
    n  = len(corpus_terms)
    df: dict[str, int] = {}
    for terms in corpus_terms:
        for t in set(terms):
            df[t] = df.get(t, 0) + 1
    return {t: math.log((n + 1) / (freq + 1)) + 1 for t, freq in df.items()}


def _tfidf_vector(tf_dict: dict[str, float],
                  idf_dict: dict[str, float],
                  vocab: list[str]) -> list[float]:
    return [tf_dict.get(t, 0.0) * idf_dict.get(t, 0.0) for t in vocab]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ── SmartMatchEngine ─────────────────────────────────────────────────────────

class SmartMatchEngine:
    """
    Drop-in pure-Python equivalent of the sklearn-based SmartMatchEngine.
    Uses TF-IDF with bigrams (ngram_range=(1,2)) and cosine similarity.

    Example
    -------
    engine = SmartMatchEngine()
    score  = engine.get_fit_score(student_profile, job_description)
    # → 95.0  (float, 0-100 scale)
    """

    def __init__(self, ngram_range: tuple[int, int] = (1, 2)):
        self.ngram_range = ngram_range

    def get_fit_score(self, student_profile: str, job_description: str) -> float:
        """
        Compute TF-IDF cosine similarity between one student profile
        and one job description.

        Returns
        -------
        float : score in [0, 100] rounded to 2 decimal places.
        """
        s_terms = _build_terms(student_profile, self.ngram_range)
        j_terms = _build_terms(job_description, self.ngram_range)

        idf   = _idf([s_terms, j_terms])
        vocab = sorted(idf.keys())

        sv = _tfidf_vector(_tf(s_terms), idf, vocab)
        jv = _tfidf_vector(_tf(j_terms), idf, vocab)

        return round(_cosine(sv, jv) * 100, 2)

    def batch_scores(self, student_profile: str,
                     job_descriptions: list[str]) -> list[float]:
        """Score one student against multiple job descriptions efficiently."""
        all_terms = [_build_terms(t, self.ngram_range)
                     for t in [student_profile] + job_descriptions]
        idf   = _idf(all_terms)
        vocab = sorted(idf.keys())

        vectors = [_tfidf_vector(_tf(terms), idf, vocab) for terms in all_terms]
        sv = vectors[0]
        return [round(_cosine(sv, vectors[i + 1]) * 100, 2)
                for i in range(len(job_descriptions))]


# ── Convenience function (backward-compatible) ────────────────────────────────

# Module-level singleton — avoids re-instantiation on every call
_engine = SmartMatchEngine()


def ml_fit_score(student_profile: str, job_descs: list[str]) -> list[int]:
    """
    Compute integer fit scores (0-100) for a student against multiple jobs.
    Backward-compatible with the previous ml_fit_score() API.
    """
    if not job_descs:
        return []
    return [int(round(s)) for s in _engine.batch_scores(student_profile, job_descs)]


# ── Quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = SmartMatchEngine()

    student = ("Python machine learning XGBoost data science deep learning "
               "NLP scikit-learn pandas CGPA 8.5 projects recommendation system")

    jobs = [
        "Data Scientist: Python machine learning scikit-learn pandas required",
        "ML Engineer: Python XGBoost deep learning NLP production models",
        "Web Developer: React JavaScript HTML CSS frontend",
        "Backend Engineer: Node.js Express MongoDB REST API microservices",
        "Data Analyst: SQL Power BI Excel statistics reporting",
    ]

    print("─" * 60)
    print(f"{'Score':>6}  Job Description")
    print("─" * 60)
    for job in jobs:
        score = engine.get_fit_score(student, job)
        bar   = "█" * int(score / 5)
        print(f"{score:>5.1f}%  {bar}  {job[:45]}")
    print("─" * 60)

    # Batch API
    batch = ml_fit_score(student, jobs)
    print("\nBatch int scores:", batch)
