import re

from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.number_reader import read_int, read_digits

_AMT = r"[0-9០-៩]+(?:,[0-9០-៩]{3})*(?:\.[0-9០-៩]+)?"
_CUR = r"\$|៛|USD|KHR|ដុល្លារ|រៀល|dollars?|riels?"


def _currency(tok: str):
    t = tok.lower()
    if tok == "$" or tok == "ដុល្លារ" or t in ("usd", "dollar", "dollars"):
        return "ដុល្លារ", "សេន"
    return "រៀល", None  # ៛, KHR, riel(s), រៀល


class MoneyNormalizer(BaseNormalizer):
    category = "MONEY"

    def __init__(self):
        self.before = re.compile(
            rf"(?<![A-Za-z0-9០-៩])({_CUR})\s*({_AMT})(?![0-9០-៩])", re.IGNORECASE
        )
        self.after = re.compile(
            rf"(?<![0-9០-៩])({_AMT})\s*({_CUR})(?![A-Za-z])", re.IGNORECASE
        )
        self.pattern = self.before  # satisfies the base contract

    def _read(self, amount: str, tok: str) -> str:
        cur, sub = _currency(tok)
        amt = khmer_to_arabic(amount).replace(",", "")
        whole_s, _, frac_s = amt.partition(".")
        whole = int(whole_s) if whole_s else 0

        if frac_s and sub:                       # dollars with cents
            cents = int((frac_s + "00")[:2])
            if whole == 0 and cents > 0:
                return read_int(cents) + sub
            out = read_int(whole) + cur
            if cents > 0:
                out += read_int(cents) + sub
            return out
        if frac_s:                               # currency without subunit + decimal (rare)
            return read_int(whole) + cur + "ក្បៀស" + read_digits(frac_s)
        return read_int(whole) + cur

    def _expand_before(self, m):
        return self._read(m.group(2), m.group(1))

    def _expand_after(self, m):
        return self._read(m.group(1), m.group(2))

    def expand(self, m):  # used for the "before" pattern
        return self._expand_before(m)

    def rules(self):
        return [
            (self.before, self._safe(self._expand_before)),
            (self.after, self._safe(self._expand_after)),
        ]

    @staticmethod
    def _safe(fn):
        def wrap(m):
            try:
                return fn(m)
            except Exception:
                return m.group(0)
        return wrap

    def normalize(self, text: str) -> str:
        text = self.before.sub(self._safe(self._expand_before), text)
        text = self.after.sub(self._safe(self._expand_after), text)
        return text