"""Découpage du texte en phrases. Utilise spaCy si un modèle est
installé, sinon un splitter regex simple (dégradation gracieuse pour
rester 100% offline sans téléchargement obligatoire de modèle).
"""
from __future__ import annotations

import re

from app.models import Sentence

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9\"«])")
_MIN_SENTENCE_LEN = 15

_nlp = None
_nlp_loaded = False


def _get_spacy_nlp(model_name: str = "fr_core_news_sm"):
    global _nlp, _nlp_loaded
    if _nlp_loaded:
        return _nlp
    _nlp_loaded = True
    try:
        import spacy

        _nlp = spacy.load(model_name, disable=["ner", "parser", "lemmatizer"])
        _nlp.enable_pipe("senter") if "senter" in _nlp.pipe_names else _nlp.add_pipe("sentencizer")
    except Exception:
        _nlp = None
    return _nlp


def split_page_into_sentences(text: str, page_number: int, start_index: int) -> list[Sentence]:
    """Découpe le texte d'une page en objets Sentence, filtre les phrases
    trop courtes (bruit de mise en page résiduel).
    """
    nlp = _get_spacy_nlp()
    raw_sentences: list[str]

    if nlp is not None:
        raw_sentences = [s.text.strip() for s in nlp(text).sents]
    else:
        raw_sentences = _SENTENCE_BOUNDARY_RE.split(text)

    sentences = []
    idx = start_index
    for raw in raw_sentences:
        cleaned = raw.strip()
        if len(cleaned) < _MIN_SENTENCE_LEN:
            continue
        sentences.append(Sentence(text=cleaned, page=page_number, index=idx))
        idx += 1
    return sentences
