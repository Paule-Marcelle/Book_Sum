"""Maximal Marginal Relevance : sélectionne un sous-ensemble de phrases
qui maximise la pertinence tout en minimisant la redondance, pour éviter
un résumé composé de phrases répétitives (voir section 10 du cahier des
charges : "coverage").
"""
from __future__ import annotations

import numpy as np


def select_mmr(
    relevance_scores: np.ndarray,
    similarity_matrix: np.ndarray,
    k: int,
    lambda_param: float = 0.7,
) -> list[int]:
    """Retourne les indices des `k` phrases sélectionnées, dans l'ordre
    de sélection (pas l'ordre du texte).

    lambda_param proche de 1 -> privilégie la pertinence.
    lambda_param proche de 0 -> privilégie la diversité.
    """
    n = len(relevance_scores)
    k = min(k, n)
    if k <= 0:
        return []

    selected: list[int] = []
    remaining = set(range(n))

    while len(selected) < k and remaining:
        best_idx, best_score = None, -np.inf
        for idx in remaining:
            redundancy = max((similarity_matrix[idx][j] for j in selected), default=0.0)
            mmr_score = lambda_param * relevance_scores[idx] - (1 - lambda_param) * redundancy
            if mmr_score > best_score:
                best_score, best_idx = mmr_score, idx
        selected.append(best_idx)
        remaining.discard(best_idx)

    return selected


def position_scores(n: int) -> np.ndarray:
    """Favorise légèrement le début et la fin d'une section (souvent les
    phrases les plus informatives : intro/conclusion)."""
    if n == 0:
        return np.array([])
    positions = np.linspace(0, 1, n)
    return 1 - 4 * (positions - 0.5) ** 2 * 0.5  # forme en U atténuée, reste dans ~[0.5, 1]
