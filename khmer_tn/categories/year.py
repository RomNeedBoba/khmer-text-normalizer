import re

from .base import BaseNormalizer

ERAS = {
    "ព": "ពុទ្ធសករាជ",    # Buddhist Era
    "គ": "គ្រិស្តសករាជ",  # Christian / Common Era
}


class YearNormalizer(BaseNormalizer):
    category = "YEAR"
    # <ព|គ> . ស [.]   with optional spaces around the dots
    pattern = re.compile(r"([ពគ])\s*\.\s*ស\s*\.?")

    def expand(self, match: re.Match) -> str:
        return ERAS[match.group(1)]