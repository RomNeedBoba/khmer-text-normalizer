KHMER_DIGITS = "០១២៣៤៥៦៧៨៩"
ARABIC_DIGITS = "0123456789"

K2A = {k: a for k, a in zip(KHMER_DIGITS, ARABIC_DIGITS)}
A2K = {a: k for k, a in zip(ARABIC_DIGITS, KHMER_DIGITS)}

# Characters we silently strip when reading a number token.
_STRIP = {",", " ", "\u00a0", "\u200b", "_"}


def is_khmer_digit(ch: str) -> bool:
    return ch in K2A


def is_digit(ch: str) -> bool:
    """True for either a Khmer or an Arabic digit."""
    return ch in K2A or ch in A2K


def khmer_to_arabic(s: str) -> str:
    """Replace any Khmer digits in `s` with Arabic digits, leave the rest."""
    return "".join(K2A.get(ch, ch) for ch in s)


def arabic_to_khmer(s: str) -> str:
    """Replace any Arabic digits in `s` with Khmer digits, leave the rest."""
    return "".join(A2K.get(ch, ch) for ch in s)


def to_int(value) -> int:
    """Parse a numeric token (Khmer or Arabic, with grouping marks) to int.

    Examples
    --------
    to_int("១២៣")   -> 123
    to_int("1,234") -> 1234
    to_int(42)      -> 42
    """
    if isinstance(value, int):
        return value
    s = "".join(ch for ch in str(value) if ch not in _STRIP)
    s = khmer_to_arabic(s)
    return int(s)
