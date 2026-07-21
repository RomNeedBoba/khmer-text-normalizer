import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

PREFIX = "ទី"


class OrdinalNormalizer(BaseNormalizer):
    category = "ORDINAL"
    # ទី, optional whitespace, then a run of Khmer or Arabic digits.
    pattern = re.compile(r"ទី\s*([០-៩0-9]+)")

    def expand(self, match: re.Match) -> str:
        number = to_int(match.group(1))
        return PREFIX + read_int(number)
