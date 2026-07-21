import re

from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.number_reader import read_int, read_digits

UNITS = {
    "km/h": "គីឡូម៉ែត្រក្នុងមួយម៉ោង", "km/hr": "គីឡូម៉ែត្រក្នុងមួយម៉ោង",
    "km²": "គីឡូម៉ែត្រការ៉េ", "km2": "គីឡូម៉ែត្រការ៉េ",
    "m²": "ម៉ែត្រការ៉េ", "m2": "ម៉ែត្រការ៉េ",
    "km": "គីឡូម៉ែត្រ", "cm": "សង់ទីម៉ែត្រ", "mm": "មិល្លីម៉ែត្រ",
    "kg": "គីឡូក្រាម", "mg": "មិល្លីក្រាម",
    "ml": "មិល្លីលីត្រ", "ha": "ហិកតា",
    "°C": "អង្សាសេ", "℃": "អង្សាសេ",
    "°F": "អង្សាហ្វារិនហៃ", "℉": "អង្សាហ្វារិនហៃ",
    "m": "ម៉ែត្រ", "g": "ក្រាម", "t": "តោន",
    "l": "លីត្រ", "L": "លីត្រ", "°": "ដឺក្រេ",
}

_AMT = r"[0-9០-៩]+(?:,[0-9០-៩]{3})*(?:\.[0-9០-៩]+)?"
_UNIT = "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True))


def _read_amount(amount: str) -> str:
    amt = khmer_to_arabic(amount).replace(",", "")
    whole_s, _, frac_s = amt.partition(".")
    whole = int(whole_s) if whole_s else 0
    return read_int(whole) + (("ក្បៀស" + read_digits(frac_s)) if frac_s else "")


class MeasureNormalizer(BaseNormalizer):
    category = "MEASURE"
    pattern = re.compile(rf"(?<![0-9០-៩])({_AMT})\s*({_UNIT})(?![A-Za-z0-9០-៩])")

    def expand(self, match: re.Match) -> str:
        return _read_amount(match.group(1)) + UNITS[match.group(2)]