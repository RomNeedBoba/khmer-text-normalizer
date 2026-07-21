import re

from .base import BaseNormalizer

LONG_CHARS = "។៕.!?"
MEDIUM_CHARS = "៖:;"
SHORT_CHARS = ",\u2013\u2014"  # ASCII comma + en-dash + em-dash

_ALL = LONG_CHARS + MEDIUM_CHARS + SHORT_CHARS


class PauseNormalizer(BaseNormalizer):
    category = "PAUSE"

    def __init__(
        self,
        mode: str = "ssml",
        long_break: str = "500ms",
        medium_break: str = "300ms",
        short_break: str = "200ms",
    ):
        if mode not in ("ssml", "symbolic", "preserve", "strip"):
            raise ValueError(f"Unknown pause mode: {mode!r}")
        self.mode = mode
        self.long_break = long_break
        self.medium_break = medium_break
        self.short_break = short_break
        self.pattern = re.compile(f"[{re.escape(_ALL)}]")

    def _marker(self, ch: str) -> str:
        if self.mode == "preserve":
            return ch
        if self.mode == "strip":
            return " "
        if ch in LONG_CHARS:
            kind, t = "long", self.long_break
        elif ch in MEDIUM_CHARS:
            kind, t = "medium", self.medium_break
        else:
            kind, t = "short", self.short_break
        if self.mode == "ssml":
            return f' <break time="{t}"/> '
        return {"long": " ||| ", "medium": " || ", "short": " | "}[kind]

    def expand(self, match: re.Match) -> str:
        return self._marker(match.group(0))

    def normalize(self, text: str) -> str:
        if self.mode == "preserve":
            return text
        return re.sub(r" {2,}", " ", super().normalize(text)).strip()