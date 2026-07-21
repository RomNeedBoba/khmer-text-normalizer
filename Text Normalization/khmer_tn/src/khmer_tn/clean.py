"""Stage 1 — CLEAN

Character-level cleanup that must run before tagging, so the category
regexes see well-formed input.

Covers:
  * Unicode NFC normalization
  * zero-width chars (ZWSP U+200B, ZWNJ U+200C, ZWJ U+200D, BOM U+FEFF)
  * NBSP and other space variants -> plain space
  * control characters
  * common lookalike / legacy substitutions (configurable map)
  * collapsed repeated Khmer diacritics (កាាាត់ -> កាត់, រយះះះ -> រយះ)
  * collapsed repeated punctuation (!!!?? -> !?)
  * whitespace deduplication

Optionally delegates deep encoding reordering (coeng order, vowel order per
the Unicode Khmer encoding spec) to the `khmernormalizer` package when it is
installed; this stage never requires it.
"""

import re
import unicodedata

# zero-width & invisible characters
_ZW = "\u200b\u200c\u200d\ufeff\u2060"

# space variants -> ASCII space
_SPACES = {
    "\u00a0": " ", "\u2000": " ", "\u2001": " ", "\u2002": " ",
    "\u2003": " ", "\u2004": " ", "\u2005": " ", "\u2006": " ",
    "\u2007": " ", "\u2008": " ", "\u2009": " ", "\u200a": " ",
    "\u202f": " ", "\u205f": " ", "\u3000": " ",
}

# frequent typo / legacy substitutions in real-world Khmer text
DEFAULT_REPLACEMENTS = {
    "ឲ្យ": "ឱ្យ",        # deprecated spelling of "to give / let"
    "\u17a4": "អា",       # deprecated independent vowel QAA
    "\u17a8": "ឧក",       # deprecated ligature QUK
    "\u17b2": "\u17b1",   # QOO TYPE TWO -> QOO TYPE ONE
    "\u17dd": "\u17d1",   # obsolete ATTHACAN -> VIRIAM
    "…": "។",             # ellipsis usually ends a sentence in web text
}

# Khmer diacritics / signs that are never legitimately doubled
_KH_DIACRITICS = (
    "\u17b6-\u17d3\u17dd"  # dependent vowels + signs (ា..៓ + ៝)
)

_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_REPEAT_DIACRITIC = re.compile(rf"([{_KH_DIACRITICS}])\1+")
_REPEAT_PUNCT = re.compile(r"([!?។៕៖,;:])\1+")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")


class Cleaner:
    def __init__(
        self,
        remove_zero_width: bool = True,
        replacements: "dict[str, str] | None" = None,
        collapse_repeats: bool = True,
        use_khmernormalizer: bool = False,
    ):
        self.remove_zero_width = remove_zero_width
        self.replacements = (
            dict(DEFAULT_REPLACEMENTS) if replacements is None else dict(replacements)
        )
        self.collapse_repeats = collapse_repeats

        self._deep = None
        if use_khmernormalizer:
            try:
                from khmernormalizer import normalize as _deep  # type: ignore
                self._deep = _deep
            except ImportError:
                pass  # optional dependency; built-in cleaning still applies

    def clean(self, text: str) -> str:
        text = unicodedata.normalize("NFC", text)
        text = _CTRL.sub("", text)

        if self.remove_zero_width:
            text = text.translate({ord(c): None for c in _ZW})
        text = text.translate({ord(k): v for k, v in _SPACES.items()})

        for old, new in self.replacements.items():
            text = text.replace(old, new)

        if self.collapse_repeats:
            text = _REPEAT_DIACRITIC.sub(r"\1", text)
            text = _REPEAT_PUNCT.sub(r"\1", text)

        if self._deep is not None:
            text = self._deep(text)

        text = _MULTI_SPACE.sub(" ", text)
        return text.strip()

    # allow use as a pipeline stage
    __call__ = clean
