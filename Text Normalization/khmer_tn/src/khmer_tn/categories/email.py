import re

from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.letter_names import spell
from ..utils.number_reader import read_int

AT = "អាត់"
DOT = "ចុច"


class EmailNormalizer(BaseNormalizer):
    category = "EMAIL"
    pattern = re.compile(
        r"(?<![A-Za-z0-9._%+\-])"
        r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
        r"(?![A-Za-z0-9])"
    )
    _token = re.compile(r"[A-Za-z]+|[0-9០-៩]+|@|\.|.")

    def __init__(self, spell_local: bool = True, spell_domain: bool = True):
        self.spell_local = spell_local
        self.spell_domain = spell_domain

    def expand(self, match: re.Match) -> str:
        s = match.group(0)
        local, _, domain = s.partition("@")

        def render(part: str, do_spell: bool) -> str:
            out = []
            for t in self._token.findall(part):
                if t == ".":
                    out.append(DOT)
                elif re.fullmatch(r"[0-9០-៩]+", t):
                    out.append(" ".join(read_int(int(c)) for c in khmer_to_arabic(t)))
                elif re.fullmatch(r"[A-Za-z]+", t):
                    out.append(spell(t) if do_spell else t)
                else:
                    out.append(t)
            return " ".join(out)

        return render(local, self.spell_local) + " " + AT + " " + render(domain, self.spell_domain)