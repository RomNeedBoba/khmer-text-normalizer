LETTER_NAMES = {
    "A": "អេ",      "B": "ប៊ី",      "C": "ស៊ី",      "D": "ឌី",
    "E": "អ៊ី",      "F": "អេហ្វ",    "G": "ជី",      "H": "អេច",
    "I": "អាយ",    "J": "ជេ",      "K": "ខេ",      "L": "អែល",
    "M": "អឹម",    "N": "អែន",     "O": "អូ",      "P": "ភី",
    "Q": "ឃ្យូ",     "R": "អា",      "S": "អេស",    "T": "ធី",
    "U": "យូ",      "V": "វី",       "W": "ដាប់ប៊ែលយូ", "X": "អែក្ស",
    "Y": "វ៉ាយ",    "Z": "ហ្ស៊ែត",
}


def letter_name(ch: str) -> str:
    """Return the Khmer name of a single Latin letter (case-insensitive).
    Non-letters are returned unchanged."""
    return LETTER_NAMES.get(ch.upper(), ch)


def spell(s: str) -> str:
    """Spell every Latin letter in `s` as its Khmer name, joined by spaces.
    Non-letters are kept as-is. Useful for IDs and email domain parts."""
    return " ".join(letter_name(c) if c.isascii() and c.isalpha() else c for c in s)