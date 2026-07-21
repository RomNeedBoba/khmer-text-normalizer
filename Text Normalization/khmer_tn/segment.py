"""Stage 4 — SEGMENT

Word segmentation for the acoustic-model input. Runs LAST, after
verbalization, because verbalization changes the text.

Backends (auto-detected, best available wins):
  * "khmercut"  — CRF segmenter (pip install khmercut), best quality
  * "regex"     — script-run splitter: separates Khmer runs from
                  Latin/digit runs and punctuation. No word boundaries
                  inside a Khmer run, but guarantees clean token edges.
  * "none"      — pass-through

Force a backend with Segmenter(backend="regex").
"""

import re

_RUN = re.compile(
    r"[\u1780-\u17ff]+"      # Khmer run
    r"|[A-Za-z]+"            # Latin run
    r"|[0-9]+"               # digit run (should be rare after verbalization)
    r"|<[^>]+>"              # SSML tags from PauseNormalizer, kept intact
    r"|[^\s\u1780-\u17ffA-Za-z0-9<]"  # single punctuation char
)


class Segmenter:
    def __init__(self, backend: str = "auto", separator: str = " "):
        self.separator = separator
        self._cut = None

        if backend in ("auto", "khmercut"):
            try:
                from khmercut import tokenize  # type: ignore
                self._cut = tokenize
                self.backend = "khmercut"
                return
            except ImportError:
                if backend == "khmercut":
                    raise ImportError(
                        "backend='khmercut' requested but khmercut is not "
                        "installed: pip install khmercut"
                    )
        self.backend = "none" if backend == "none" else "regex"

    def segment(self, text: str) -> str:
        if self.backend == "none":
            return text

        out_tokens: "list[str]" = []
        # protect SSML tags (they may contain spaces), segment the rest
        for chunk in re.split(r"(<[^>]+>)", text):
            if chunk.startswith("<") and chunk.endswith(">"):
                out_tokens.append(chunk)               # SSML tag, kept intact
                continue
            for part in chunk.split():
                for run in _RUN.findall(part):
                    if self._cut is not None and re.match(r"[\u1780-\u17ff]", run):
                        out_tokens.extend(self._cut(run))
                    else:
                        out_tokens.append(run)
        return self.separator.join(t for t in out_tokens if t)

    __call__ = segment
