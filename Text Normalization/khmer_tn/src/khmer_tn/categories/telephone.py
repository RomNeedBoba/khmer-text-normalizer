import re
from .base import BaseNormalizer
from ..utils.digits import khmer_to_arabic
from ..utils.number_reader import read_int

_SEP = r"[ \u00a0\-]"
_D = "[0-9០-៩]"

class TelephoneNormalizer(BaseNormalizer):
    category = "TELEPHONE"
    pattern = re.compile(
        rf"(?<![0-9០-៩A-Za-z+])\+?(?:855|៨៥៥|[0០])(?:{_SEP}?{_D}){{6,11}}(?![0-9០-៩])"
    )

    def expand(self, match: re.Match) -> str:
        raw = match.group(0)
        digits = "".join(c for c in khmer_to_arabic(raw) if c.isdigit())

        # Isolate the prefix (855 or 0) from the subscriber digits
        if digits.startswith("855"):
            prefix_digits = "855"
            subscriber = digits[3:]
        else:
            prefix_digits = digits[0]  # This will be "0"
            subscriber = digits[1:]

        # Validate length (8 remaining digits for a 9-digit number, 9 for a 10-digit number)
        if not (8 <= len(subscriber) <= 9):
            return raw

        # Process the prefix digit-by-digit to keep '855' or '0' behavior exactly the same
        spoken_parts = [read_int(int(c)) for c in prefix_digits]

        # Apply your custom chunking rules to the subscriber digits
        if len(subscriber) == 8:
            # 9-Digit Rule (e.g., 0 12 345 678)
            # Sliced as: [2 digits], [3 digits], [3 digits]
            chunks = [
                subscriber[0:2],
                subscriber[2:5],
                subscriber[5:8]
            ]
        else:
            # 10-Digit Rule (e.g., 0 12 90 80 126)
            # Sliced as: [2 digits], [2 digits], [2 digits], [3 digits]
            chunks = [
                subscriber[0:2],
                subscriber[2:4],
                subscriber[4:6],
                subscriber[6:9]
            ]

        # Convert each chunk into an integer so read_int calculates the magnitude (hundreds/tens)
        spoken_parts.extend(read_int(int(chunk)) for chunk in chunks)

        spoken = " ".join(spoken_parts)
        return ("បូក " + spoken) if "+" in raw else spoken