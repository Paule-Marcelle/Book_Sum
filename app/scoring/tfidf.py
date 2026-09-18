"""Scores TF-IDF et similarité cosinus entre phrases (base commune de
TextRank et MMR en mode STRICT CONFIDENTIEL).
"""
from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

FRENCH_STOPWORDS = frozenset(
    """
    au aux avec ce ces dans de des du elle en et eux il je la le leur lui
    ma mais me même mes moi mon ne nos notre nous on ou par pas pour qu que
    qui sa se ses son sur ta te tes toi ton tu un une vos votre vous c d j
    l à m n s t y été étée étées étés étant suis es est sommes êtes sont
    """.split()
)


def build_tfidf_matrix(sentences: list[str]) -> np.ndarray:
    """Retourne la matrice TF-IDF dense (n_phrases x vocab)."""
    vectorizer = TfidfVectorizer(stop_words=list(FRENCH_STOPWORDS), min_df=1)
    matrix = vectorizer.fit_transform(sentences)
    return matrix.toarray()


def tfidf_sentence_scores(sentences: list[str]) -> np.ndarray:
    """Score chaque phrase par la somme de ses poids TF-IDF (proxy de
    densité informative), normalisé entre 0 et 1.
    """
    if len(sentences) < 2:
        return np.ones(len(sentences))
    matrix = build_tfidf_matrix(sentences)
    scores = matrix.sum(axis=1)
    max_score = scores.max() or 1.0
    return scores / max_score


def cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normalized = matrix / norms
    return normalized @ normalized.T
