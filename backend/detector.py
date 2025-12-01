# backend/detector.py

from __future__ import annotations

import json
import re
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Any

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .prompts import build_phi_prompt


#  can change this model to a different local one if you prefer
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"   # use your pulled model


@dataclass
class Replacement:
    original: str
    tag: str
    category: str | None = None


@dataclass
class PHIResult:
    deidentified_note: str
    replacements: List[Replacement] = field(default_factory=list)
    raw_llm_output: str | None = None


def _call_llm(prompt: str) -> str:
    """
    Call the local Ollama LLM server using the /generate endpoint.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()



def _parse_llm_json_output(raw: str, original_note: str) -> PHIResult:
    """
    Parse JSON reliably, even if the model wraps it in quotes or prints text before/after.
    """

    # 1. If output starts with a quoted JSON string, try to unquote it
    if raw.startswith('"') and raw.endswith('"'):
        try:
            raw = json.loads(raw)
        except Exception:
            pass

    # 2. Extract JSON substring using regex (handles messy model output)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    # 3. Try to parse JSON strictly
    try:
        data = json.loads(raw)
    except Exception:
        return PHIResult(
            deidentified_note=original_note,
            replacements=[],
            raw_llm_output=raw,
        )

    # 4. Extract fields
    deid = data.get("deidentified_note", original_note)
    repls = data.get("replacements", [])

    replacements = []
    for item in repls:
        replacements.append(
            Replacement(
                original=item.get("original", ""),
                tag=item.get("tag", ""),
                category=item.get("category", None),
            )
        )

    return PHIResult(
        deidentified_note=deid,
        replacements=replacements,
        raw_llm_output=raw,
    )


def detect_phi(note: str) -> PHIResult:
    """
    High-level function:
    - Build prompt from note
    - Call LLM
    - Parse structured output
    """
    prompt = build_phi_prompt(note)
    raw_output = _call_llm(prompt)
    result = _parse_llm_json_output(raw_output, original_note=note)
    return result
