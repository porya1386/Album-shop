"""Pure-Python helpers for the products search bar (no Django imports,
so they are easy to test).

The search box accepts several words. Every word must match (AND), and a
word matches when it is found in the NAME, or equals the PRICE, or equals
the creation YEAR.   Example:  "sunset 2024"  or  "forest 150"
"""
import re
from decimal import Decimal, InvalidOperation

# Persian / Arabic-Indic digits -> ASCII, so "۲۰۲۴" works like "2024"
_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

YEAR_MIN, YEAR_MAX = 1000, 2999
MAX_TERMS = 6            # ignore anything after this many words
MAX_TERM_LEN = 60
MAX_NUMBER = Decimal("999999999")   # keeps SQLite/DB integer limits safe


def normalize(text):
    return (text or "").translate(_DIGITS).strip()


def parse_number(text):
    """'1,200' / '12.5' / '$40' -> Decimal, otherwise None."""
    t = normalize(text).lstrip("$€£").replace(",", "")
    if not re.fullmatch(r"\d+(\.\d+)?", t):
        return None
    try:
        value = Decimal(t)
    except InvalidOperation:
        return None
    return value if value <= MAX_NUMBER else None


def parse_terms(q):
    """Split the search text into term dicts:
    {'text': 'forest', 'number': None, 'year': None}
    'number' is set when the word is numeric (can be a price),
    'year' is set when it also looks like a 4-digit year."""
    terms = []
    for word in normalize(q).split():
        word = word[:MAX_TERM_LEN]
        number = parse_number(word)
        year = None
        if number is not None and number == number.to_integral_value():
            if YEAR_MIN <= int(number) <= YEAR_MAX and len(word.lstrip("$€£")) == 4:
                year = int(number)
        terms.append({"text": word, "number": number, "year": year})
        if len(terms) >= MAX_TERMS:
            break
    return terms
