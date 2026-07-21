"""REPEAT — the Khmer repetition sign ៗ (U+17D7).

ផ្សេងៗ must be spoken as ផ្សេង ផ្សេង. The sign repeats the PRECEDING word,
so this stage needs word boundaries:

  * with khmercut installed: segments the preceding Khmer run and repeats
    only the last word
  * fallback: repeats the whole preceding contiguous Khmer run (correct for
    single words, over-repeats glued compounds — acceptable degradation)

Runs as a full-text pass after verbalization, before PAUSE/SEGMENT.
"""

import re

from .base import BaseNormalizer

_KH_RUN = re.compile(r"([\u1780-\u17d3\u17dc\u17dd]+)\s*ៗ")


class RepeatNormalizer(BaseNormalizer):
    category = "REPEAT"
    pattern = _KH_RUN

    def __init__(self):
        try:
            from khmercut import tokenize  # type: ignore
            self._cut = tokenize
        except ImportError:
            self._cut = None

    def expand(self, match: re.Match) -> str:
        run = match.group(1)
        if self._cut is not None:
            tokens = [t for t in self._cut(run) if t.strip()]
            if tokens:
                return run + " " + tokens[-1]
        return run + " " + run

    def normalize(self, text: str) -> str:
        # iterate: ចម្រុះៗៗ -> repeated twice
        prev = None
        while prev != text:
            prev = text
            text = self.pattern.sub(self._expand_safe, text, count=0)
            if "ៗ" not in text:
                break
        return text
