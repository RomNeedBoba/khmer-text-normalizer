import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

CONNECTOR = "ដល់"  # "to / until"  (use "ទៅ" for an alternative)

_INT = r"(?:[1-9១-៩][0-9០-៩]*|[0០])"  # cardinal operand, no leading zero


class RangeNormalizer(BaseNormalizer):
    category = "RANGE"

    def __init__(self, connector: str = CONNECTOR):
        self.connector = connector
        self.pattern = re.compile(
            rf"(?<![0-9០-៩.\-\u2013\u2014])({_INT})[-\u2013\u2014]({_INT})"
            rf"(?![0-9០-៩.\-\u2013\u2014])"
        )

    def expand(self, match: re.Match) -> str:
        a = read_int(to_int(match.group(1)))
        b = read_int(to_int(match.group(2)))
        return a + self.connector + b