"""CARDINAL  (category 01)

Reads bare integer quantities as Khmer words, using the shared number engine
(utils/number_reader.py).

CARDINAL is the catch-all for numbers not claimed by a more specific category,
so in the pipeline it runs LAST and is deliberately conservative: it only
matches genuine integers and leaves anything ambiguous for the categories that
own it (DECIMAL, RANGE, ID, ...).

Matches
-------
  * plain integers (Khmer ០-៩ or Arabic 0-9):   ៥ -> ប្រាំ,  123 -> មួយរយម្ភៃបី
  * comma-grouped integers (groups of 3):       1,234 -> មួយពាន់ពីររយសាមសិបបួន
  * a standalone zero:                          ០ -> សូន្យ

Deliberately NOT matched (left for other categories / later steps)
------------------------------------------------------------------
  * leading-zero runs like 007  (codes / IDs)
  * a leading +/- sign          (RANGE / signed handling)
  * any fragment of a longer digit token (boundary lookarounds enforce this)
"""

import re

from .base import BaseNormalizer
from ..utils.digits import to_int
from ..utils.number_reader import read_int

_PATTERN = re.compile(
    r"""
    (?<![0-9០-៩])                                  # left boundary: no digit before
    (?:
        [1-9១-៩][0-9០-៩]{0,2}(?:,[0-9០-៩]{3})+     # grouped:  1,234 / 12,345
      | [0០]                                        # standalone zero
      | [1-9១-៩][0-9០-៩]*                           # plain integer (no leading zero)
    )
    (?![0-9០-៩])                                    # right boundary: no digit after
    """,
    re.VERBOSE,
)


class CardinalNormalizer(BaseNormalizer):
    category = "CARDINAL"
    pattern = _PATTERN

    def expand(self, match: re.Match) -> str:
        return read_int(to_int(match.group(0)))