# backend/validator.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import spacy


# Load spaCy English model once
_nlp = spacy.load("en_core_web_sm")


# Entity labels we treat as "suspicious" PHI
POTENTIAL_PHI_LABELS = {
    "PERSON",
    "ORG",
    "GPE",
    "LOC",
    "FAC",
    "NORP",
    "DATE",
    "TIME",
    "CARDINAL",
}


@dataclass
class DetectedEntity:
    text: str
    label: str
    start_char: int
    end_char: int


@dataclass
class ValidationResult:
    has_remaining_phi: bool
    entities: List[DetectedEntity] = field(default_factory=list)


def validate_note(note: str) -> ValidationResult:
    """
    Run a lightweight NER pass to check if any obvious PHI-like entities remain.
    This is not perfect, but acts as a safety net on top of the LLM output.
    """
    doc = _nlp(note)
    entities: List[DetectedEntity] = []

    for ent in doc.ents:
        if ent.label_ in POTENTIAL_PHI_LABELS:
            entities.append(
                DetectedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                )
            )

    has_phi = len(entities) > 0
    return ValidationResult(has_remaining_phi=has_phi, entities=entities)
