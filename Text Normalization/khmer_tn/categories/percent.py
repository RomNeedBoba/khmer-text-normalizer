import re

from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.number_reader import read_int, read_digits

_SIGNS = {"%": "ភាគរយ", "‰": "ភាគពាន់"}
_AMT = r"[0-9០-៩]+(?:,[0-9០-៩]{3})*(?:\.[0-9០-៩]+)?"


class PercentNormalizer(BaseNormalizer):
    category = "PERCENT"
    pattern = re.compile(rf"(?<![0-9០-៩])({_AMT})\s*([%‰])")

    def expand(self, match: re.Match) -> str:
        amt = khmer_to_arabic(match.group(1)).replace(",", "")
        whole_s, _, frac_s = amt.partition(".")
        whole = int(whole_s) if whole_s else 0
        num = read_int(whole) + (("ក្បៀស" + read_digits(frac_s)) if frac_s else "")
        return num + _SIGNS[match.group(2)]