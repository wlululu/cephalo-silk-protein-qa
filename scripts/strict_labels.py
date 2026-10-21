"""Task-specific strict categorical-label normalization.

Identical rule to the validated evaluation: whole response label only; lower
case, surrounding whitespace and terminal punctuation are ignored. Do not
extract labels from explanatory paragraphs in the primary benchmark.
"""
import re
import pandas as pd

YES_NO_QUESTIONS = {
    'Does this protein contain alpha-helix?',
    'Does this protein contain beta-sheet?',
    'Does this protein contain coil?',
    'Is the protein hydrophobic (GRAVY > 0)?',
    'Is the protein predicted to be stable (instability index ≤ 40)?',
}
PREDOMINANT = 'Which secondary structure is most prevalent?'
ACIDIC = 'Is the protein acidic (pI < 7) or basic (pI > 7)?'
LABELS = {q: {'yes', 'no'} for q in YES_NO_QUESTIONS}
LABELS[PREDOMINANT] = {'alpha-helix', 'beta-sheet', 'coil'}
LABELS[ACIDIC] = {'acidic', 'basic', 'neutral'}


def normalize_short_label(response, question):
    """Return complete canonical label, else None. Do not infer semantics."""
    if pd.isna(response) or question not in LABELS:
        return None
    cleaned = str(response).strip().lower()
    cleaned = re.sub(r'[\s.!?;,。！？；，]+$', '', cleaned).strip()
    return cleaned if cleaned in LABELS[question] else None
