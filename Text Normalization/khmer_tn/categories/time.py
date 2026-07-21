import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

HOUR = "ម៉ោង"
MINUTE = "នាទី"
SECOND = "វិនាទី"

# day-period words (broadcast convention), used when period=True
def _period(h24: int) -> str:
    if 5 <= h24 <= 11:  return "ព្រឹក"
    if h24 == 12:       return "ថ្ងៃត្រង់"
    if 13 <= h24 <= 16: return "រសៀល"
    if 17 <= h24 <= 18: return "ល្ងាច"
    return "យប់"        # 19-23, 0-4

_D = "[0-9០-៩]"


class TimeNormalizer(BaseNormalizer):
    category = "TIME"

    def __init__(self, period: bool = False):
        # period=True converts 24h to 12h and appends ព្រឹក/ថ្ងៃត្រង់/រសៀល/ល្ងាច/យប់
        self.period = period
        self.pattern = re.compile(
            rf"(?:ម៉ោង\s*)?(?<![0-9០-៩])({_D}{{1,2}}):({_D}{{2}})(?::({_D}{{2}}))?(?![0-9០-៩])"
        )

    def expand(self, match: re.Match) -> str:
        h = to_int(match.group(1))
        m = to_int(match.group(2))
        s = to_int(match.group(3)) if match.group(3) else None
        if not (0 <= h <= 23 and 0 <= m <= 59 and (s is None or 0 <= s <= 59)):
            return match.group(0)
        suffix = ""
        if self.period:
            suffix = _period(h)
            h12 = h % 12
            h = 12 if h12 == 0 else h12
        out = HOUR + read_int(h)
        if m:
            out += " " + read_int(m) + MINUTE
        if s:
            out += " " + read_int(s) + SECOND
        return out + suffix