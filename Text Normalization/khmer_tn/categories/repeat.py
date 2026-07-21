"""REPEAT — the Khmer repetition sign ៗ (U+17D7).

ផ្សេងៗ must be spoken as ផ្សេង ផ្សេង. The sign repeats the PRECEDING word,
so this stage needs word boundaries:

  * with khmercut installed: segments the preceding Khmer run and repeats
    only the last word (exact)
  * fallback: approximates the last word from the last two "orthographic
    syllable" chunks of the run (base consonant + optional coeng-subscript
    + optional dependent vowels/signs). A syllable's own trailing bare
    consonant commonly splits off as its own chunk, so two chunks
    reconstruct one real syllable; two chunks also happen to cover most
    genuine two-syllable words. Verified against single-syllable words
    (ថ្មី), two-syllable words (ចម្រុះ), and words whose last syllable ends
    in a bare consonant (ផ្សេង). Still a heuristic, not a real segmenter —
    an unusual 3+ syllable word right before ៗ can still be under-captured.

Runs as a full-text pass after verbalization, before PAUSE/SEGMENT.
"""

import re

from .base import BaseNormalizer

_KH_RUN = re.compile(r"([\u1780-\u17d3\u17dc\u17dd]+)\s*ៗ")

# one Khmer "orthographic syllable": base consonant/independent vowel,
# optional coeng+subscript-consonant(s), optional trailing dependent
# vowels/signs (same sign range clean.py already treats as one class)
_SYLLABLE = re.compile(
    r"[\u1780-\u17a2\u17a5-\u17b3]"
    r"(?:\u17d2[\u1780-\u17a2])*"
    r"[\u17b6-\u17d3\u17dd]*"
)
_FALLBACK_SYLLABLES = 2  # empirically covers 1- and 2-syllable words


class RepeatNormalizer(BaseNormalizer):
    category = "REPEAT"
    pattern = _KH_RUN

    def __init__(self):
        try:
            from khmercut import tokenize  # type: ignore
            self._cut = tokenize
        except ImportError:
            self._cut = None

    def _last_word_guess(self, run: str) -> str:
        chunks = _SYLLABLE.findall(run)
        return "".join(chunks[-_FALLBACK_SYLLABLES:]) if chunks else run

    def expand(self, match: re.Match) -> str:
        run = match.group(1)
        if self._cut is not None:
            tokens = [t for t in self._cut(run) if t.strip()]
            if tokens:
                return run + " " + tokens[-1]
        return run + " " + self._last_word_guess(run)

    def normalize(self, text: str) -> str:
        # iterate: ចម្រុះៗៗ -> repeated twice
        prev = None
        while prev != text:
            prev = text
            text = self.pattern.sub(self._expand_safe, text, count=0)
            if "ៗ" not in text:
                break
        return text
