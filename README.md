# Book Summarizer — synthèse documentaire confidentielle

Moteur de résumé extractif hiérarchique pour documents volumineux (livres,
rapports 1000+ pages), conçu pour tourner **entièrement en local** : aucun
document n'est envoyé à un LLM ou une API externe.

Architecture détaillée : voir la conversation d'origine dans `debo.md` (du
projet source). Ci-dessous, la version implémentée.

## Comment ça marche

```
PDF/EPUB → extraction texte (+OCR si scanné) → nettoyage
        → détection des chapitres (TOC ou regex) → découpage en phrases
        → scoring (TF-IDF + TextRank + position [+ embeddings locaux])
        → sélection MMR (pertinence + diversité, anti-redondance)
        → résumé par section → par chapitre → résumé global
```

Le résumé est **extractif** : chaque phrase du résumé est une phrase du
document original, avec sa page source conservée (onglet "Passages
sourcés" de l'app).

## Deux modes

| Mode | Techniques | Dépendances |
|---|---|---|
| **STRICT CONFIDENTIEL** | TF-IDF + TextRank + MMR + position | `requirements.txt` uniquement |
| **LOCAL NLP+** | + embeddings sémantiques locaux (Sentence-Transformers) | + `requirements-optional.txt` |

Les deux modes sont 100 % offline après installation — aucun appel réseau
lors de l'analyse d'un document.

## Installation locale

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# optionnel : mode LOCAL NLP+ et découpage de phrases via spaCy
pip install -r requirements-optional.txt
```

Pour l'OCR des PDF scannés, installer le binaire **Tesseract** (pas
seulement le paquet Python `pytesseract`) :
- Windows : https://github.com/UB-Mannheim/tesseract/wiki
- Linux/Streamlit Cloud : géré via `packages.txt` (déjà présent dans ce repo)

## Lancer l'app

```bash
streamlit run streamlit_app.py
```

## Tests

```bash
pip install pytest
pytest
```

## Déploiement sur Streamlit Community Cloud

1. Pousser ce dossier sur un dépôt GitHub (public ou privé).
2. Aller sur https://share.streamlit.io, connecter le dépôt GitHub.
3. Renseigner :
   - **Main file path** : `streamlit_app.py`
   - **Python version** : 3.11 (ou celle utilisée en local)
4. Streamlit Cloud installe automatiquement `requirements.txt` et
   `packages.txt` (paquets apt, ici Tesseract OCR).
5. Ne pas activer `requirements-optional.txt` sur le tier gratuit : le mode
   LOCAL NLP+ (Sentence-Transformers/torch) dépasse souvent la limite de
   mémoire (1 Go) du free tier. Pour ce mode, préférer un hébergement avec
   plus de RAM (Streamlit Cloud "Teams", VM dédiée, ou usage local).

⚠️ Le fichier `debo.md` (contenant potentiellement des notes internes) et
tout PDF de test ne doivent pas être commit si le contenu est confidentiel
— vérifier `.gitignore` avant de pousser.

## Limites connues (à communiquer au client)

- Résumé **extractif**, pas génératif : pas de reformulation, le système
  sélectionne les phrases les plus représentatives.
- La détection de chapitres dépend de la table des matières native du PDF
  ou de motifs regex (`Chapitre N`, `Chapter N`, `N. Titre`...) ; un livre
  à la mise en page atypique peut nécessiter un ajustement des motifs dans
  `app/structure.py`.
- L'OCR (mode PDF scanné) ralentit fortement le traitement sur les gros
  documents.
