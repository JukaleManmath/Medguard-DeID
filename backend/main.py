# backend/main.py

from __future__ import annotations

from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .detector import detect_phi, Replacement
from .validator import validate_note, ValidationResult
from .utils import strip_extra_whitespace


app = FastAPI(
    title="Medguard – LLM-Based De-Identification Agent",
    description="Prototype API for PHI removal in clinical notes.",
    version="0.1.0",
)


# ---------- Pydantic response / request models ----------


class ReplacementModel(BaseModel):
    original: str
    tag: str
    category: str | None = None

    @classmethod
    def from_det(cls, r: Replacement) -> "ReplacementModel":
        return cls(original=r.original, tag=r.tag, category=r.category)


class DetectedEntityModel(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int


class ValidationResultModel(BaseModel):
    has_remaining_phi: bool
    entities: List[DetectedEntityModel]


class DeidentifyRequest(BaseModel):
    note: str


class DeidentifyResponse(BaseModel):
    deidentified_note: str
    replacements: List[ReplacementModel]
    validation: ValidationResultModel
    raw_llm_output: str | None = None


# ------------------- Routes -----------------------------


@app.get("/health")
def health_check():
    return {"status": "ok", "detail": "Medguard backend is running"}


@app.post("/deidentify", response_model=DeidentifyResponse)
def deidentify_endpoint(payload: DeidentifyRequest):
    """
    Main endpoint: takes a clinical note, returns de-identified note +
    replacements list + validator result.
    """
    note = payload.note

    # 1) LLM-based PHI detection & replacement
    phi_result = detect_phi(note)
    deid_note = strip_extra_whitespace(phi_result.deidentified_note)

    # 2) Validation pass
    val_result: ValidationResult = validate_note(deid_note)

    entities_models = [
        DetectedEntityModel(
            text=e.text,
            label=e.label,
            start_char=e.start_char,
            end_char=e.end_char,
        )
        for e in val_result.entities
    ]

    validation_model = ValidationResultModel(
        has_remaining_phi=val_result.has_remaining_phi,
        entities=entities_models,
    )

    replacements_models = [
        ReplacementModel.from_det(r) for r in phi_result.replacements
    ]

    return DeidentifyResponse(
        deidentified_note=deid_note,
        replacements=replacements_models,
        validation=validation_model,
        raw_llm_output=phi_result.raw_llm_output,
    )
