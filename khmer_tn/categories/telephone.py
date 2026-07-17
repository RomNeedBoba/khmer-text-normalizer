import re

from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.number_reader import read_int

_SEP = r"[ \u00a0\-]"
_D = "[0-9០-៩]"


class TelephoneNormalizer(BaseNormalizer):
    category = "TELEPHONE"
    pattern = re.compile(
        rf"(?<![0-9០-៩A-Za-z+])\+?(?:855|៨៥៥|[0០])(?:{_SEP}?{_D}){{6,11}}(?![0-9០-៩])"
    )

    def expand(self, match: re.Match) -> str:
        raw = match.group(0)
        digits = "".join(c for c in khmer_to_arabic(raw) if c.isdigit())

        if digits.startswith("855"):
            valid = 8 <= len(digits) - 3 <= 9          # national part after 855
        else:
            valid = 9 <= len(digits) <= 10             # leading-0 form
        if not valid:
            return raw

        spoken = " ".join(read_int(int(c)) for c in digits)
        return ("បូក " + spoken) if "+" in raw else spoken