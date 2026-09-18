import numpy as np

from app.scoring.mmr import select_mmr
from app.scoring.textrank import textrank_scores
from app.scoring.tfidf import build_tfidf_matrix, cosine_similarity_matrix
from app.summarizer import MODE_STRICT, extract_summary
from app.models import Sentence


def test_textrank_scores_sum_reasonable():
    sentences = [
        "Le chat mange une souris.",
        "Le chien aboie sur le facteur.",
        "Le chat dort sur le canape.",
        "Les enfants jouent dans le jardin.",
    ]
    matrix = build_tfidf_matrix(sentences)
    sim = cosine_similarity_matrix(matrix)
    scores = textrank_scores(sim)
    assert len(scores) == len(sentences)
    assert scores.max() == 1.0
    assert (scores >= 0).all()


def test_mmr_avoids_duplicate_selection():
    # phrase 0 = la plus pertinente. phrase 2 quasi identique a 0 (redondante,
    # malgre une pertinence proche). phrase 3 differente mais moins pertinente.
    relevance = np.array([1.0, 0.9, 0.95, 0.3])
    similarity = np.array(
        [
            [1.0, 0.95, 0.95, 0.1],
            [0.95, 1.0, 0.9, 0.1],
            [0.95, 0.9, 1.0, 0.1],
            [0.1, 0.1, 0.1, 1.0],
        ]
    )
    selected = select_mmr(relevance, similarity, k=2, lambda_param=0.5)
    # la redondance avec la phrase 0 doit ecarter la phrase 2 au profit de la 3
    assert selected == [0, 3]


def test_extract_summary_returns_subset_in_order():
    sentences = [
        Sentence(text=f"Ceci est la phrase numero {i} du document de test.", page=1, index=i)
        for i in range(20)
    ]
    summary = extract_summary(sentences, ratio=0.3, mode=MODE_STRICT)
    assert 0 < len(summary) <= len(sentences)
    indices = [s.index for s in summary]
    assert indices == sorted(indices)
