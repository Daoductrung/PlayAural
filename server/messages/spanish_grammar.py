"""Spanish conjunction rules shared by list formatting and Fluent messages.

Rules follow the RAE Diccionario panhispánico de dudas (entries "y" and "o").
Both changes depend on how the next word is pronounced, not only on spelling:

* ``y`` becomes ``e`` before the sound /i/ (``Ana e Isabel``, ``B 5 e I 20``,
  ``Hilda``). It stays ``y`` when that /i/ forms a diphthong with the next
  vowel (``madera y hierro``, ``agua y hielo``). Words such as ``hiato`` or
  ``ion`` accept both pronunciations; this module keeps ``y`` for them. The
  stressed interrogative ``¿Y Inés?`` is not a conjunction and never changes.
* ``o`` becomes ``u`` before the sound /o/, spelled ``o-`` or ``ho-``
  (``siete u ocho``, ``N 33 u O 70``, ``mujer u hombre``), and also between
  numbers written with digits when the number is read starting with /o/
  (``7000 u 8000``: ``ocho mil``). Digits starting with 8 are read ``ocho...``.
  ``11`` (``once``) follows the same sound principle, although the DPD does not
  list it.

A currency sign before an amount is not read first (``$88`` is "ochenta y ocho
dólares"), so ``u $88`` is used. When the next word cannot be classified
(symbols such as ``+8`` that are read aloud), the plain ``y``/``o`` is kept.

Babel's CLDR list patterns and plain ``{ $a } y { $b }`` Fluent placeholders do
not apply these rules, so the helpers below do it at format time.
"""

from __future__ import annotations

import re
from collections.abc import Sequence


# English loanwords spelled with an initial "ho" whose "h" is aspirated. They
# do not start with the vowel sound /o/, so "o" stays "o". Whole words only:
# prefixes would also catch Spanish "hotel" or "homenaje".
_ASPIRATED_HO_WORDS = frozenset(
    {
        "hobby",
        "hobbies",
        "hockey",
        "hooligan",
        "hooligans",
        "hot",
        "home",
        "hold",
        "hold'em",
        "holdem",
        "holding",
    }
)

# Unaccented strong vowels. "i" followed by one of these (or by the same vowel
# with an accent) is a semi-consonant ("yo"-like), not the vowel /i/.
_STRONG_VOWELS = "aeouáéóú"

_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
_NUMBER_RE = re.compile(r"\d[\d.,]*")
# "11" is read "once" (also 11 000, 11 000 000, and 11,5 -> "once coma cinco").
_ELEVEN_RE = re.compile(r"11(?:\.000)*(?!\d)")


# Characters that are not read aloud, so the sound is decided by what follows:
# quotes, brackets, inverted marks and the invisible Unicode bidi/format marks.
_SILENT_LEADING = frozenset(
    "\"'\u201c\u201d\u2018\u2019\u00ab\u00bb()[]{}\u00bf\u00a1"
    "\u2066\u2067\u2068\u2069\u200b\u200e\u200f\u2060\ufeff"
    # Currency signs written before an amount: NVDA reads "$88" as "ochenta y
    # ocho dólares", so the number decides the sound.
    "$\u20ac\u00a3\u00a5"
)


def _leading_text(text: object) -> str:
    """Return the text after silent leading characters.

    Whitespace and the silent characters above are skipped. Anything else that
    is not a letter or digit (``+8`` is read "más ocho", ``-8`` "menos ocho")
    stops the search and returns an empty string, so the caller keeps the plain "y"/"o" instead of
    guessing a sound.
    """
    value = str(text)
    index = 0
    while index < len(value) and (
        value[index].isspace() or value[index] in _SILENT_LEADING
    ):
        index += 1
    if index >= len(value) or not value[index].isalnum():
        return ""
    return value[index:]


def starts_with_i_sound(text: object) -> bool:
    """Return True when ``text`` starts with the vowel sound /i/."""
    rest = _leading_text(text)
    if not rest or rest[0].isdigit():
        return False
    match = _TOKEN_RE.match(rest)
    if match is None:
        return False
    token = match.group(0)
    lowered = token.lower()
    if token[0] == "I" and len(token) > 1 and token.isupper():
        # Acronyms such as "IA" are spelled out, so they start with "i".
        return True
    if lowered.startswith("hí"):
        return True
    if lowered.startswith("hi"):
        following = lowered[2:3]
        return following not in tuple(_STRONG_VOWELS)
    if lowered[0] == "í":
        return True
    if lowered[0] == "i":
        following = lowered[1:2]
        return following not in tuple(_STRONG_VOWELS)
    return False


def starts_with_o_sound(text: object) -> bool:
    """Return True when ``text`` starts with the vowel sound /o/."""
    rest = _leading_text(text)
    if not rest:
        return False
    if rest[0].isdigit():
        number = _NUMBER_RE.match(rest)
        digits = number.group(0) if number else rest[0]
        return digits.startswith("8") or _ELEVEN_RE.match(digits) is not None
    match = _TOKEN_RE.match(rest)
    if match is None:
        return False
    lowered = match.group(0).lower()
    if lowered[0] in "oó":
        return True
    if lowered.startswith(("ho", "hó")):
        return lowered.replace("’", "'") not in _ASPIRATED_HO_WORDS
    return False


def spanish_and(next_text: object) -> str:
    """Return ``e`` before an /i/ sound, otherwise ``y``."""
    return "e" if starts_with_i_sound(next_text) else "y"


def spanish_or(next_text: object) -> str:
    """Return ``u`` before an /o/ sound, otherwise ``o``."""
    return "u" if starts_with_o_sound(next_text) else "o"


def fix_list_conjunction(
    text: str, items: Sequence[object], conjunction: str
) -> str:
    """Correct the final conjunction of an already formatted Spanish list.

    ``text`` is what Babel produced for ``items`` and ``conjunction`` is the
    plain ``"y"`` or ``"o"`` it used. Only the conjunction right before the last
    item is touched, and only when ``text`` really ends with it.
    """
    if len(items) < 2 or conjunction not in ("y", "o"):
        return text
    last = str(items[-1])
    corrected = (
        spanish_and(last) if conjunction == "y" else spanish_or(last)
    )
    if corrected == conjunction:
        return text
    plain = f" {conjunction} {last}"
    if not text.endswith(plain):
        return text
    return f"{text[: len(text) - len(plain)]} {corrected} {last}"
