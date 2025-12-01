

# **MedGuard — PHI De-Identification Backend**

MedGuard is a lightweight backend service that removes Protected Health Information (PHI) from clinical text using a locally-run LLM (via Ollama) and a spaCy validator.
It replaces sensitive spans with structured tags (e.g., `[PATIENT_NAME]`, `[DATE]`) while preserving all non-PHI clinical meaning.

## 🚀 Features

* FastAPI backend for PHI de-identification
* Local LLM inference (Ollama)
* Strict JSON-structured prompting
* spaCy validator to detect remaining PHI
* Zero paraphrasing — only PHI is replaced
* Clean and simple API (`POST /deidentify`)

## 📁 Project Structure

```
backend/
├── main.py        # FastAPI entrypoint
├── detector.py    # LLM call + JSON parsing
├── prompts.py     # Structured prompts
├── validator.py   # spaCy PHI validator
└── utils.py       # Helper functions
```

## ⚙️ Setup

### Create environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install spaCy model

```bash
python -m spacy download en_core_web_sm
```

### Start Ollama

```bash
ollama pull llama3
```

## ▶️ Run the API

```bash
uvicorn backend.main:app --reload
```

API runs at:

```
http://localhost:8000/deidentify
```

## 🧪 Example Request

```json
{
  "note": "Patient John Smith visited Boston Medical Center on 03/15/2024."
}
```

## 📦 Example Response

```json
{
  "deidentified_note": "Patient [PATIENT_NAME] visited [HOSPITAL] on [DATE].",
  "replacements": [...],
  "validation": {...}
}
```
