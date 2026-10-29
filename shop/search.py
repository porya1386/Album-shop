
"""Pure-Python helpers for the products search bar."""

import re
from decimal import Decimal, InvalidOperation

# Persian and Arabic-Indic digits -> ASCII
_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)

YEAR_MIN, YEAR_MAX = 1000, 2999
MAX_TERMS = 6
MAX_TERM_LEN = 60

# Maximum signed 64-bit integer, compatible with SQLite integer storage.
MAX_NUMBER = Decimal("9223372036854775807")


def normalize(text):
    return (text or "").translate(_DIGITS).strip()


def parse_number(text):
    """
    Accept numbers with or without thousands separators.

    Examples:
    1200000
    1,200,000
    ۱۲۰۰۰۰۰
    ۱٬۲۰۰٬۰۰۰
    $1,200,000
    12.5
    """
    t = normalize(text).strip()

    # Remove optional currency symbols.
    t = t.lstrip("$€£").strip()

    # Remove thousands separators and normalize decimal separator.
    t = (
        t.replace(",", "")
         .replace("٬", "")
         .replace("،", "")
         .replace("\u00a0", "")
         .replace("٫", ".")
    )

    # Correct regex: optional decimal fraction, without **.
    if not re.fullmatch(r"\d+(?:\.\d+)?", t):
        return None

    try:
        value = Decimal(t)
    except InvalidOperation:
        return None

    if not value.is_finite() or value > MAX_NUMBER:
        return None

    return value


def parse_terms(q):
    """
    Split search text into terms.
    Every term must match a searchable field.
    """
    terms = []

    for word in normalize(q).split():
        word = word[:MAX_TERM_LEN]
        number = parse_number(word)

        # Detect a four-digit year.
        year_text = (
            word.lstrip("$€£")
                .replace(",", "")
                .replace("٬", "")
                .replace("،", "")
                .strip()
        )

        year = None
        if (
            number is not None
            and number == number.to_integral_value()
            and YEAR_MIN <= int(number) <= YEAR_MAX
            and year_text.isdigit()
            and len(year_text) == 4
        ):
            year = int(number)

        terms.append({
            "text": word,
            "number": number,
            "year": year,
        })

        if len(terms) >= MAX_TERMS:
            break

    return terms
