import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

HOUR = "ម៉ោង"
MINUTE = "នាទី"
SECOND = "វិនាទី"

_D = "[0-9០-៩]"


class TimeNormalizer(BaseNormalizer):
    category = "TIME"

    def __init__(self):
        self.pattern = re.compile(
            rf"(?:ម៉ោង\s*)?(?<![0-9០-៩])({_D}{{1,2}}):({_D}{{2}})(?::({_D}{{2}}))?(?![0-9០-៩])"
        )

    def expand(self, match: re.Match) -> str:
        h = to_int(match.group(1))
        m = to_int(match.group(2))
        s = to_int(match.group(3)) if match.group(3) else None
        if not (0 <= h <= 23 and 0 <= m <= 59 and (s is None or 0 <= s <= 59)):
            return match.group(0)
        out = HOUR + read_int(h)
        if m:
            out += " " + read_int(m) + MINUTE
        if s:
            out += " " + read_int(s) + SECOND
        return out