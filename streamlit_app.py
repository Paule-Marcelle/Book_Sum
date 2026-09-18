"""Interface Streamlit du moteur de synthèse documentaire confidentiel.

Tout le traitement (parsing, OCR, scoring, embeddings) s'exécute dans le
processus Streamlit : aucun document n'est envoyé à un service externe.
"""
from __future__ import annotations

import streamlit as st

from app import pipeline, summarizer
from app.scoring import embeddings as emb

st.set_page_config(page_title="Book Summarizer confidentiel", page_icon="📖", layout="wide")

MODE_LABELS = {
    "STRICT CONFIDENTIEL (TF-IDF + TextRank + MMR, sans modèle NLP)": summarizer.MODE_STRICT,
    "LOCAL NLP+ (ajoute des embeddings locaux Sentence-Transformers)": summarizer.MODE_LOCAL_NLP_PLUS,
}


def main() -> None:
    st.title("📖 Moteur de synthèse documentaire confidentiel")
    st.caption(
        "Résumé extractif hiérarchique de livres/documents volumineux — 100 % local, "
        "aucune donnée envoyée à un LLM externe."
    )

    with st.sidebar:
        st.header("Paramètres")
        mode_label = st.radio("Mode de confidentialité", list(MODE_LABELS.keys()))
        mode = MODE_LABELS[mode_label]
        if mode == summarizer.MODE_LOCAL_NLP_PLUS and not emb.is_available():
            st.warning(
                "sentence-transformers n'est pas installé ou le modèle n'a pas pu être "
                "chargé — le système bascule automatiquement en mode STRICT CONFIDENTIEL."
            )
        ocr_enabled = st.checkbox("Activer l'OCR pour les pages scannées (Tesseract)", value=True)
        st.divider()
        st.caption("Voir `debo.md` pour l'architecture complète du système.")

    uploaded_file = st.file_uploader("Dépose un PDF (livre, rapport, document long)", type=["pdf"])

    if uploaded_file is None:
        st.info("Choisis un fichier PDF pour lancer l'analyse.")
        return

    if st.button("Lancer l'analyse", type="primary"):
        pdf_bytes = uploaded_file.read()
        title = uploaded_file.name.rsplit(".", 1)[0]

        with st.spinner("Extraction et structuration du document..."):
            book = pipeline.build_book(pdf_bytes, title=title, ocr=ocr_enabled)

        if not book.chapters:
            st.error("Aucun texte exploitable n'a été trouvé dans ce PDF.")
            return

        st.session_state["book"] = book
        with st.spinner(f"Résumé hiérarchique en cours ({len(book.chapters)} chapitre(s) détecté(s))..."):
            st.session_state["result"] = pipeline.summarize_book(book, mode=mode)

    result = st.session_state.get("result")
    book = st.session_state.get("book")
    if result is None or book is None:
        return

    st.success(f"Analyse terminée — {len(book.chapters)} chapitre(s), {len(book.all_sentences)} phrases indexées.")

    tabs = st.tabs(
        ["Résumé express", "Résumé standard", "Résumé détaillé", "Par chapitre", "Points clés", "Passages sourcés"]
    )

    with tabs[0]:
        st.subheader("Résumé express (~1 page)")
        st.write(result.express)

    with tabs[1]:
        st.subheader("Résumé standard (~5-10 pages)")
        st.write(result.standard)

    with tabs[2]:
        st.subheader("Résumé détaillé (~20-30 pages)")
        st.write(result.detailed)

    with tabs[3]:
        st.subheader("Résumé par chapitre")
        for chapter_title, chapter_summary in result.by_chapter:
            with st.expander(chapter_title):
                st.write(chapter_summary)

    with tabs[4]:
        st.subheader("Points clés")
        for point in result.key_points:
            st.markdown(f"- {point}")

    with tabs[5]:
        st.subheader("Passages sourcés")
        st.caption("Chaque phrase du résumé standard, avec sa page d'origine dans le document.")
        for text, page in result.sourced_excerpts:
            st.markdown(f"> {text}\n\n**Source : p. {page}**")

    st.divider()
    export_text = (
        f"# {book.title}\n\n## Résumé express\n{result.express}\n\n"
        f"## Résumé standard\n{result.standard}\n\n## Résumé détaillé\n{result.detailed}\n\n"
        "## Par chapitre\n"
        + "\n".join(f"### {t}\n{s}" for t, s in result.by_chapter)
        + "\n\n## Points clés\n"
        + "\n".join(f"- {p}" for p in result.key_points)
    )
    st.download_button(
        "Télécharger le résumé complet (Markdown)",
        data=export_text,
        file_name=f"{book.title}_resume.md",
        mime="text/markdown",
    )


if __name__ == "__main__":
    main()
