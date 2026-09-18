"""TextRank : construit un graphe de similarité entre phrases et applique
PageRank pour obtenir un score de centralité par phrase.
"""
from __future__ import annotations

import networkx as nx
import numpy as np


def textrank_scores(similarity_matrix: np.ndarray, damping: float = 0.85) -> np.ndarray:
    """Retourne un score TextRank normalisé (0-1) par phrase."""
    n = similarity_matrix.shape[0]
    if n == 0:
        return np.array([])
    if n == 1:
        return np.array([1.0])

    graph = nx.from_numpy_array(similarity_matrix)
    try:
        ranks = nx.pagerank(graph, alpha=damping, max_iter=200)
    except nx.PowerIterationFailedConvergence:
        ranks = {i: 1.0 / n for i in range(n)}

    scores = np.array([ranks[i] for i in range(n)])
    max_score = scores.max() or 1.0
    return scores / max_score
