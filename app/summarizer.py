"""Résumé extractif d'un ensemble de phrases : combine TextRank, TF-IDF,
position et (en mode LOCAL NLP+) similarité sémantique par embeddings,
puis sélectionne les phrases via MMR pour limiter la redondance.

Correspond aux sections 6-10 du cahier des charges (debo.md).
"""
from __future__ import annotations

import numpy as np

from app.models import Sentence
from app.scoring import embeddings as emb
from app.scoring import mmr as mmr_module
from app.scoring import tfidf as tfidf_module
from app.scoring import textrank as textrank_module

MODE_STRICT = "strict_confidentiel"
MODE_LOCAL_NLP_PLUS = "local_nlp_plus"

# Pondérations par défaut (section 7). En mode STRICT, le poids sémantique
# est redistribué sur TextRank/TF-IDF puisqu'aucun embedding n'est calculé.
WEIGHTS_WITH_SEMANTIC = {"textrank": 0.40, "tfidf": 0.25, "position": 0.15, "semantic": 0.20}
WEIGHTS_NO_SEMANTIC = {"textrank": 0.50, "tfidf": 0.35, "position": 0.15, "semantic": 0.0}


def score_sentences(
    sentences: list[Sentence], mode: str = MODE_STRICT
) -> tuple[np.ndarray, np.ndarray]:
    """Retourne (scores_finaux, matrice_similarite) pour une liste de phrases."""
    texts = [s.text for s in sentences]
    n = len(texts)
    if n == 0:
        return np.array([]), np.zeros((0, 0))
    if n == 1:
        return np.array([1.0]), np.array([[1.0]])

    tfidf_matrix = tfidf_module.build_tfidf_matrix(texts)
    similarity_matrix = tfidf_module.cosine_similarity_matrix(tfidf_matrix)

    textrank_score = textrank_module.textrank_scores(similarity_matrix)
    tfidf_score = tfidf_module.tfidf_sentence_scores(texts)
    position_score = mmr_module.position_scores(n)

    semantic_score = np.zeros(n)
    weights = WEIGHTS_NO_SEMANTIC
    if mode == MODE_LOCAL_NLP_PLUS and emb.is_available():
        sentence_embeddings = emb.embed_sentences(texts)
        if sentence_embeddings is not None:
            centroid = sentence_embeddings.mean(axis=0)
            centroid = centroid / (np.linalg.norm(centroid) or 1.0)
            semantic_score = emb.semantic_similarity_scores(sentence_embeddings, centroid)
            weights = WEIGHTS_WITH_SEMANTIC
            # la similarité sémantique donne aussi une matrice de redondance plus fine
            similarity_matrix = sentence_embeddings @ sentence_embeddings.T

    final_scores = (
        weights["textrank"] * textrank_score
        + weights["tfidf"] * tfidf_score
        + weights["position"] * position_score
        + weights["semantic"] * semantic_score
    )
    return final_scores, similarity_matrix


def extract_summary(
    sentences: list[Sentence],
    ratio: float = 0.1,
    min_sentences: int = 1,
    max_sentences: int | None = None,
    mode: str = MODE_STRICT,
    lambda_param: float = 0.7,
) -> list[Sentence]:
    """Sélectionne les phrases les plus représentatives et les retourne
    dans leur ordre d'origine (pour rester lisible)."""
    if not sentences:
        return []

    scores, similarity_matrix = score_sentences(sentences, mode=mode)
    k = max(min_sentences, round(len(sentences) * ratio))
    if max_sentences is not None:
        k = min(k, max_sentences)

    selected_indices = mmr_module.select_mmr(scores, similarity_matrix, k, lambda_param)
    selected_indices.sort()
    return [sentences[i] for i in selected_indices]
