import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

MONTHS = {
    1: "មករា", 2: "កុម្ភៈ", 3: "មីនា", 4: "មេសា",
    5: "ឧសភា", 6: "មិថុនា", 7: "កក្កដា", 8: "សីហា",
    9: "កញ្ញា", 10: "តុលា", 11: "វិច្ឆិកា", 12: "ធ្នូ",
}

_D = "[0-9០-៩]"


class DateNormalizer(BaseNormalizer):
    category = "DATE"

    def __init__(self, month_as_name: bool = True):
        self.month_as_name = month_as_name
        self.iso = re.compile(
            rf"(?:ថ្ងៃទី\s*)?(?<![0-9០-៩])({_D}{{4}})-({_D}{{1,2}})-({_D}{{1,2}})(?![0-9០-៩])"
        )
        self.dmy = re.compile(
            rf"(?:ថ្ងៃទី\s*)?(?<![0-9០-៩])({_D}{{1,2}})([/-])({_D}{{1,2}})\2({_D}{{2,4}})(?![0-9០-៩])"
        )
        self.month_marker = re.compile(rf"ខែ\s*({_D}{{1,2}})(?![0-9០-៩])")
        self.pattern = self.dmy  # satisfies the base contract

    # --- helpers -----------------------------------------------------------
    def _month_word(self, month: int) -> str:
        return MONTHS[month] if self.month_as_name else read_int(month)

    def _full_date(self, day: int, month: int, year: int):
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return None
        return f"ថ្ងៃទី{read_int(day)} ខែ{self._month_word(month)} ឆ្នាំ{read_int(year)}"

    def _expand_iso(self, m):
        out = self._full_date(to_int(m.group(3)), to_int(m.group(2)), to_int(m.group(1)))
        return out if out is not None else m.group(0)

    def _expand_dmy(self, m):
        out = self._full_date(to_int(m.group(1)), to_int(m.group(3)), to_int(m.group(4)))
        return out if out is not None else m.group(0)

    def _expand_month(self, m):
        month = to_int(m.group(1))
        return "ខែ" + self._month_word(month) if 1 <= month <= 12 else m.group(0)

    def expand(self, match):  # used for the dmy pattern
        return self._expand_dmy(match)

    @staticmethod
    def _safe(fn):
        def wrap(m):
            try:
                return fn(m)
            except Exception:
                return m.group(0)
        return wrap

    def rules(self):
        return [
            (self.iso, self._safe(self._expand_iso)),
            (self.dmy, self._safe(self._expand_dmy)),
            (self.month_marker, self._safe(self._expand_month)),
        ]

    # --- pipeline ----------------------------------------------------------
    def normalize(self, text: str) -> str:
        text = self.iso.sub(self._safe(self._expand_iso), text)
        text = self.dmy.sub(self._safe(self._expand_dmy), text)
        text = self.month_marker.sub(self._safe(self._expand_month), text)
        return text