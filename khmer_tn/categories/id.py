import re

from .base import BaseNormalizer
from ..utils.letter_names import letter_name
from ..utils.number_reader import read_int


def _is_latin_alpha(c: str) -> bool:
    return c.isascii() and c.isalpha()


class IdNormalizer(BaseNormalizer):
    category = "ID"
    pattern = re.compile(
        r"(?<![A-Za-z0-9០-៩])[A-Za-z0-9០-៩][A-Za-z0-9០-៩_\-]*(?![A-Za-z0-9០-៩])"
    )

    def expand(self, match: re.Match) -> str:
        s = match.group(0)
        has_letter = any(_is_latin_alpha(c) for c in s)
        has_digit = any(c.isdigit() for c in s)
        if not (has_letter and has_digit):
            return s

        out = []
        for c in s:
            if _is_latin_alpha(c):
                out.append(letter_name(c))
            elif c.isdigit():
                out.append(read_int(int(c)))
            # separators (- _ etc.) are skipped
        return " ".join(out)    