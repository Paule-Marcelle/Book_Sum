"""Embeddings de phrases via sentence-transformers, exécutés 100% en
local (aucun appel réseau après le premier téléchargement du modèle).
Utilisé uniquement en mode LOCAL NLP+. Dégrade proprement vers `None`
si le paquet n'est pas installé, pour rester utilisable en mode
STRICT CONFIDENTIEL sans dépendance supplémentaire.
"""
from __future__ import annotations

import numpy as np

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None
_model_loaded = False


def is_available() -> bool:
    return _load_model() is not None


def _load_model():
    global _model, _model_loaded
    if _model_loaded:
        return _model
    _model_loaded = True
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(_MODEL_NAME)
    except Exception:
        _model = None
    return _model


def embed_sentences(sentences: list[str]) -> np.ndarray | None:
    """Retourne une matrice (n_phrases x dim) ou None si le modèle local
    n'est pas disponible."""
    model = _load_model()
    if model is None or not sentences:
        return None
    return model.encode(sentences, show_progress_bar=False, normalize_embeddings=True)


def semantic_similarity_scores(sentence_embeddings: np.ndarray, target_embedding: np.ndarray) -> np.ndarray:
    """Similarité cosinus de chaque phrase par rapport à un vecteur cible
    (ex: centroïde du chapitre), normalisée entre 0 et 1."""
    sims = sentence_embeddings @ target_embedding
    sims = (sims + 1) / 2  # cosine in [-1,1] -> [0,1]
    return np.clip(sims, 0, 1)
