# backend/utils.py

from __future__ import annotations

from typing import List

from .detector import Replacement


def format_replacement_log(replacements: List[Replacement]) -> str:
    """
    Turn the replacement list into a human-readable multi-line string.
    Useful for debugging, logs, or your report screenshots.
    """
    if not replacements:
        return "No PHI replacements recorded."

    lines = []
    for r in replacements:
        cat = f" ({r.category})" if r.category else ""
        lines.append(f"- '{r.original}' → {r.tag}{cat}")
    return "\n".join(lines)


def strip_extra_whitespace(text: str) -> str:
    """
    Normalize whitespace a bit (collapse multiple spaces, trim ends).
    """
    return " ".join(text.split())
