from .digits import to_int, khmer_to_arabic

# 0-9
UNITS = {
    0: "សូន្យ",
    1: "មួយ",
    2: "ពីរ",
    3: "បី",
    4: "បួន",
    5: "ប្រាំ",
    6: "ប្រាំមួយ",
    7: "ប្រាំពីរ",
    8: "ប្រាំបី",
    9: "ប្រាំបួន",
}

TEN = "ដប់"  # 10 (also prefix for 11-19)

# multiples of ten, 20-90 (these are single dedicated words, not 2*10 etc.)
TENS = {
    2: "ម្ភៃ",
    3: "សាមសិប",
    4: "សែសិប",
    5: "ហាសិប",
    6: "ហុកសិប",
    7: "ចិតសិប",
    8: "ប៉ែតសិប",
    9: "កៅសិប",
}

# scale words, largest first
SCALES = [
    (1_000_000, "លាន"),
    (100_000, "សែន"),
    (10_000, "ម៉ឺន"),
    (1_000, "ពាន់"),
    (100, "រយ"),
]

MINUS = "ដក"  # spoken "minus" prefix for negative values


def read_int(n: int) -> str:
    """Read a Python int as Khmer words."""
    if n < 0:
        return MINUS + read_int(-n)
    if n < 10:
        return UNITS[n]
    if n < 20:
        return TEN + (UNITS[n - 10] if n > 10 else "")
    if n < 100:
        tens, unit = divmod(n, 10)
        return TENS[tens] + (UNITS[unit] if unit else "")
    for value, word in SCALES:
        if n >= value:
            quotient, remainder = divmod(n, value)
            return read_int(quotient) + word + (read_int(remainder) if remainder else "")
    return UNITS[0]  # unreachable, keeps type checkers happy


def read_cardinal(token) -> str:
    """Read a numeric token (str or int, Khmer or Arabic digits) as Khmer words."""
    return read_int(to_int(token))


def read_digits(token) -> str:
    """Read each digit of a token separately, in order.

    Used for the fractional part of a decimal, codes, etc. Leading zeros are
    preserved (0.05 != 0.5).

        read_digits("14")  -> "មួយបួន"
        read_digits("05")  -> "សូន្យប្រាំ"
    """
    s = khmer_to_arabic(str(token))
    return "".join(UNITS[int(ch)] for ch in s if "0" <= ch <= "9")
