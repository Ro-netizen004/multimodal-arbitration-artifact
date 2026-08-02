"""Strict, lightweight answer attribution for ChartQA-Conflict."""

import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction


YES_SYNONYMS = {"yes", "true", "correct", "affirmative"}
NO_SYNONYMS = {"no", "false", "incorrect", "negative"}
CURRENCY = {"$": "usd", "\u20ac": "eur", "\u00a3": "gbp", "\u00a5": "jpy"}
UNIT_ALIASES = {
    "%": "percent", "percent": "percent", "percentage": "percent",
    "dollar": "usd", "dollars": "usd", "usd": "usd",
    "euro": "eur", "euros": "eur", "eur": "eur",
    "pound": "gbp", "pounds": "gbp", "gbp": "gbp",
    "yen": "jpy", "jpy": "jpy",
}
SCALE_WORDS = {"thousand", "million", "billion", "trillion"}
CURRENCY_WORDS = {
    "dollar": "usd", "dollars": "usd", "usd": "usd",
    "pound": "gbp", "pounds": "gbp", "gbp": "gbp",
    "euro": "eur", "euros": "eur", "eur": "eur",
    "yen": "jpy", "jpy": "jpy",
}


def extract_final_answer(prediction):
    """Return only a marked final answer or a terse answer-only response."""
    text = str(prediction).strip()
    marked = re.search(r"####\s*([^\r\n]+)", text)
    if marked:
        return marked.group(1).strip()
    answer_line = re.fullmatch(r"(?i)(?:final\s+)?answer\s*:\s*(.+)", text)
    if answer_line:
        return answer_line.group(1).strip()
    terminal_answer = re.search(
        r"(?i)(?:therefore,?\s*)?(?:the\s+)?(?:final\s+)?answer\s+is\s+"
        r"([^\r\n.]+)\.?\s*$", text)
    if terminal_answer:
        return terminal_answer.group(1).strip()
    if "\n" not in text and len(text.split()) <= 4:
        return text
    return None


def normalize_answer(answer, unit_hint=""):
    """Canonicalize an exact answer while permitting compatible unit labels."""
    if answer is None:
        return None
    text = str(answer).strip().lower().replace("\u2212", "-").replace("\u2013", "-")
    text = text.strip(" \t\r\n\"'`.")
    if text in YES_SYNONYMS:
        return ("boolean", "yes")
    if text in NO_SYNONYMS:
        return ("boolean", "no")
    pattern = re.fullmatch(
        r"(?P<currency>[$\u20ac\u00a3\u00a5])?\s*"
        r"(?P<number>[+-]?(?:(?:\d{1,3}(?:[ ,]\d{3})+|[\d,]+)(?:\.\d+)?|"
        r"\d+\s*/\s*\d+))"
        r"\s*(?P<unit>%|[a-z][a-z.\s-]*)?", text)
    if not pattern:
        return None
    raw_number = pattern.group("number").replace(",", "").replace(" ", "")
    try:
        if "/" in raw_number:
            fraction = Fraction(raw_number)
            value = Decimal(fraction.numerator) / Decimal(fraction.denominator)
        else:
            value = Decimal(raw_number)
    except (InvalidOperation, ValueError, ZeroDivisionError):
        return None

    hinted_raw = str(unit_hint).strip().lower().replace("-", "_") or "unitless"
    hinted_parts = [UNIT_ALIASES.get(part, part)
                    for part in hinted_raw.split("_")]
    hinted = "_".join(hinted_parts)
    raw_unit = pattern.group("unit") or ""
    tokens = re.sub(r"[^a-z%]+", " ", raw_unit.lower()).strip().split()
    currencies = {CURRENCY_WORDS[token] for token in tokens
                  if token in CURRENCY_WORDS}
    symbol_currency = CURRENCY.get(pattern.group("currency"))
    if symbol_currency:
        currencies.add(symbol_currency)
    if len(currencies) > 1:
        return None
    explicit_currency = next(iter(currencies), None)
    hinted_currency = next((item for item in ("usd", "gbp", "eur", "jpy")
                            if item in hinted.split("_")), None)
    if explicit_currency and explicit_currency != hinted_currency:
        return None
    scales = {token for token in tokens if token in SCALE_WORDS}
    if len(scales) > 1:
        return None
    explicit_scale = next(iter(scales), None)
    hinted_scale = next((item for item in SCALE_WORDS
                         if item in hinted.split("_")), None)
    if explicit_scale and explicit_scale != hinted_scale:
        return None
    explicit_percent = raw_unit == "%" or any(
        token in {"percent", "percentage"} for token in tokens)
    hinted_percent = any(part in {"percent", "percentage"}
                         for part in hinted.split("_"))
    if explicit_percent and not hinted_percent:
        return None
    return ("numeric", value.normalize(), hinted)


def classify(prediction, row):
    final = extract_final_answer(prediction)
    predicted = normalize_answer(final, row.get("unit_class", ""))
    image = normalize_answer(row["image_answer"], row.get("unit_class", ""))
    text = normalize_answer(row["text_answer"], row.get("unit_class", ""))
    if predicted is None or image is None or text is None:
        return "invalid", final, predicted
    if image == text and predicted == image:
        return "ambiguous", final, predicted
    if predicted == image:
        return "image", final, predicted
    if predicted == text:
        return "text", final, predicted
    return "neither", final, predicted
