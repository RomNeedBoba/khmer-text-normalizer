"""Pipeline orchestrator.

    raw text -> CLEAN -> TAG+VERBALIZE (span-based) -> PAUSE -> SEGMENT

Tagging is span-based, NOT a destructive cascade: every category matches
against the SAME original text, candidate spans are resolved by priority
(most specific category wins on overlap), and all replacements are applied
in one pass. This fixes the cascade bugs where e.g. ORDINAL consumed the
day out of "ថ្ងៃទី 15/07/2026" before DATE could see it, or DECIMAL ate
"25.50" out of "$25.50" before MONEY ran.
"""

from .clean import Cleaner
from .segment import Segmenter
from .categories import (
    EmailNormalizer, TelephoneNormalizer, DateNormalizer, TimeNormalizer,
    DurationNormalizer, MoneyNormalizer, PercentNormalizer, MeasureNormalizer,
    FractionNormalizer, RangeNormalizer, DecimalNormalizer, OrdinalNormalizer,
    YearNormalizer, IdNormalizer, CardinalNormalizer, PauseNormalizer,
    RepeatNormalizer,
)

# most specific first — earlier categories win overlapping spans
DEFAULT_CATEGORIES = [
    EmailNormalizer,       # a@b.c must beat ID / CARDINAL
    TelephoneNormalizer,   # long digit runs, beats CARDINAL / RANGE
    DateNormalizer,        # 15/07/2026 beats FRACTION / ORDINAL / CARDINAL
    TimeNormalizer,        # 9:30 beats CARDINAL
    DurationNormalizer,    # 5 mins beats MEASURE("m") / CARDINAL
    MoneyNormalizer,       # $25.50 beats DECIMAL / CARDINAL
    PercentNormalizer,
    MeasureNormalizer,
    FractionNormalizer,    # 3/4 (after DATE so d/m/y wins)
    RangeNormalizer,       # 2020-2026 beats ID / CARDINAL
    DecimalNormalizer,
    OrdinalNormalizer,
    YearNormalizer,
    IdNormalizer,          # AB12 letter+digit codes
    CardinalNormalizer,    # catch-all, lowest priority
]


class KhmerNormalizer:
    def __init__(
        self,
        categories=None,
        cleaner: "Cleaner | None | bool" = True,
        pause: "PauseNormalizer | None | bool" = True,
        segmenter: "Segmenter | None | bool" = False,
        repeat: "RepeatNormalizer | None | bool" = True,
        decimal_convention: str = "web",
    ):
        """decimal_convention:
          "web"      -> "." decimal, "," thousands (dominant in Cambodian
                        web/social text; default)
          "official" -> "," decimal (ក្បៀស), "." thousands, per MoEYS
                        textbooks and the CLDR km locale
        """
        if categories is None:
            categories = []
            for cls in DEFAULT_CATEGORIES:
                if cls is DecimalNormalizer and decimal_convention == "official":
                    categories.append(DecimalNormalizer(decimal_sep=",", thousands_sep="."))
                else:
                    categories.append(cls())
        self.categories = list(categories)
        self.repeat = RepeatNormalizer() if repeat is True else (repeat or None)

        self.cleaner = Cleaner() if cleaner is True else (cleaner or None)
        self.pause = PauseNormalizer() if pause is True else (pause or None)
        self.segmenter = Segmenter() if segmenter is True else (segmenter or None)

    # ------------------------------------------------------------------ #
    def tag(self, text: str):
        """Return resolved, non-overlapping spans:
        [(start, end, replacement, category), ...] sorted by start."""
        claimed: "list[tuple[int, int, str, str]]" = []

        def overlaps(s: int, e: int) -> bool:
            return any(s < ce and cs < e for cs, ce, _, _ in claimed)

        for norm in self.categories:                       # priority order
            for pattern, expand in norm.rules():
                for m in pattern.finditer(text):
                    s, e = m.span()
                    if s == e or overlaps(s, e):
                        continue
                    try:
                        rep = expand(m)
                    except Exception:
                        continue
                    if rep == m.group(0):                  # declined (e.g. ID)
                        continue
                    claimed.append((s, e, rep, norm.category))
        return sorted(claimed)

    def verbalize(self, text: str) -> str:
        out, last = [], 0
        for s, e, rep, _ in self.tag(text):
            out.append(text[last:s])
            out.append(rep)
            last = e
        out.append(text[last:])
        return "".join(out)

    # ------------------------------------------------------------------ #
    def normalize(self, text: str) -> str:
        if self.cleaner is not None:
            text = self.cleaner(text)                      # 1 CLEAN
        text = self.verbalize(text)                        # 2 TAG + 3 VERBALIZE
        if self.repeat is not None:
            text = self.repeat.normalize(text)             #   ៗ duplication
        if self.pause is not None:
            text = self.pause.normalize(text)              #   pauses / SSML
        if self.segmenter is not None:
            text = self.segmenter(text)                    # 4 SEGMENT
        return text

    __call__ = normalize
