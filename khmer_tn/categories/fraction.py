import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

PART = "ភាគ"  # "part" -> joins numerator and denominator

_D = "[0-9០-៩]"


class FractionNormalizer(BaseNormalizer):
    category = "FRACTION"

    def __init__(self, part_word: str = PART, mixed_connector: str = " "):
        # mixed_connector joins the whole number and the fraction in a mixed
        # number; default is a space. Set to " និង" for "two and three-quarters".
        self.part_word = part_word
        self.mixed_connector = mixed_connector
        self.pattern = re.compile(
            rf"(?<![0-9០-៩/])(?:({_D}+)\s+)?({_D}+)/({_D}+)(?![0-9០-៩/])"
        )

    def expand(self, match: re.Match) -> str:
        whole, num, den = match.group(1), match.group(2), match.group(3)
        fraction = read_int(to_int(num)) + self.part_word + read_int(to_int(den))
        if whole:
            return read_int(to_int(whole)) + self.mixed_connector + fraction
        return fraction