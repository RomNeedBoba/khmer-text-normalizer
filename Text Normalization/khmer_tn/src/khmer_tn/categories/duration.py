import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

# abbreviation (lowercase) -> Khmer unit word
_UNITS = {
    "hours": "ម៉ោង", "hour": "ម៉ោង", "hrs": "ម៉ោង", "hr": "ម៉ោង", "h": "ម៉ោង",
    "minutes": "នាទី", "minute": "នាទី", "mins": "នាទី", "min": "នាទី",
    "seconds": "វិនាទី", "second": "វិនាទី", "secs": "វិនាទី", "sec": "វិនាទី",
    "weeks": "សប្តាហ៍", "week": "សប្តាហ៍", "wks": "សប្តាហ៍", "wk": "សប្តាហ៍",
    "months": "ខែ", "month": "ខែ", "mos": "ខែ", "mo": "ខែ",
    "years": "ឆ្នាំ", "year": "ឆ្នាំ", "yrs": "ឆ្នាំ", "yr": "ឆ្នាំ",
    "days": "ថ្ងៃ", "day": "ថ្ងៃ",
}

_D = "[0-9០-៩]"
# longest abbreviations first so "hours" beats "hour" beats "hr" beats "h"
_ABBR = "|".join(sorted(_UNITS, key=len, reverse=True))


class DurationNormalizer(BaseNormalizer):
    category = "DURATION"
    pattern = re.compile(
        rf"(?<![0-9០-៩])({_D}+)\s*({_ABBR})(?![A-Za-z])",
        re.IGNORECASE,
    )

    def expand(self, match: re.Match) -> str:
        n = read_int(to_int(match.group(1)))
        unit = _UNITS[match.group(2).lower()]
        return n + unit