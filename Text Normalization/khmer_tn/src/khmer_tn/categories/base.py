import re
from abc import ABC, abstractmethod


class BaseNormalizer(ABC):
    category: str = "BASE"
    pattern: "re.Pattern | None" = None

    @abstractmethod
    def expand(self, match: re.Match) -> str:
        """Return the spoken form for a single match."""
        raise NotImplementedError

    def rules(self):
        """(pattern, expand) pairs for span-based tagging.
        Categories with multiple patterns override this."""
        return [] if self.pattern is None else [(self.pattern, self.expand)]

    def normalize(self, text: str) -> str:
        if self.pattern is None:
            return text
        return self.pattern.sub(self._expand_safe, text)

    def _expand_safe(self, match: re.Match) -> str:
        try:
            return self.expand(match)
        except Exception:
            return match.group(0)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} category={self.category!r}>"