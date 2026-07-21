import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int, read_digits

_D = "[0-9០-៩]"  # one Khmer or Arabic digit


class DecimalNormalizer(BaseNormalizer):
    category = "DECIMAL"

    def __init__(self, decimal_sep=".", thousands_sep=",", point_word="ក្បៀស"):
        self.decimal_sep = decimal_sep
        self.thousands_sep = thousands_sep
        self.point_word = point_word

        sep = re.escape(decimal_sep)
        if thousands_sep and thousands_sep != decimal_sep:
            t = re.escape(thousands_sep)
            int_part = rf"{_D}{{1,3}}(?:{t}{_D}{{3}})+|{_D}+|"  # grouped | plain | empty
        else:
            int_part = rf"{_D}+|"                               # plain | empty

        self.pattern = re.compile(
            rf"(?<![0-9០-៩])({int_part}){sep}({_D}+)(?![0-9០-៩])"
        )

    def expand(self, match: re.Match) -> str:
        int_raw = match.group(1)
        if self.thousands_sep:
            int_raw = int_raw.replace(self.thousands_sep, "")
        n = to_int(int_raw) if int_raw else 0
        return read_int(n) + self.point_word + read_digits(match.group(2))
