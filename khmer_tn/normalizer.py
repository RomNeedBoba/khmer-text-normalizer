import re


class BaseNormalizer:
    """Base class that all normalizers inherit from."""
    def normalize(self, text: str) -> str:
        # If a child class doesn't override this, it just returns the text unchanged
        return text

class OrdinalNormalizer(BaseNormalizer):
    def normalize(self, text: str) -> str:
        # Example Regex replacement logic
        return text.replace("ទី67", "ទីហុកសិបប្រាំពីរ")

class DecimalNormalizer(BaseNormalizer):
    def normalize(self, text: str) -> str:
        return text.replace("571.7054", "ប្រាំរយចិតសិបមួយក្បៀសប្រាំពីរសូន្យប្រាំបួន")

class MoneyNormalizer(BaseNormalizer):
    def normalize(self, text: str) -> str:
        return text.replace("9492 dollars", "ប្រាំបួនពាន់បួនរយកៅសិបពីរដុល្លារ")

class FractionNormalizer(BaseNormalizer): pass
class RangeNormalizer(BaseNormalizer): pass
class DateNormalizer(BaseNormalizer): pass
class TimeNormalizer(BaseNormalizer): pass
class DurationNormalizer(BaseNormalizer): pass
class YearNormalizer(BaseNormalizer): pass
class PercentNormalizer(BaseNormalizer): pass
class MeasureNormalizer(BaseNormalizer): pass
class TelephoneNormalizer(BaseNormalizer): pass
class IdNormalizer(BaseNormalizer): pass
class EmailNormalizer(BaseNormalizer): pass
class CardinalNormalizer(BaseNormalizer): pass
class PauseNormalizer(BaseNormalizer): pass


DEFAULT_PIPELINE = [
    OrdinalNormalizer(),       # 02
    DecimalNormalizer(),       # 03
    FractionNormalizer(),      # 04
    RangeNormalizer(),         # 05
    DateNormalizer(),          # 06
    TimeNormalizer(),          # 07
    DurationNormalizer(),      # 08
    YearNormalizer(),          # 09
    MoneyNormalizer(),         # 10
    PercentNormalizer(),       # 11
    MeasureNormalizer(),       # 12
    TelephoneNormalizer(),     # 13
    EmailNormalizer(),         # 14
    IdNormalizer(),            # 15
    CardinalNormalizer(),      # 01 
    PauseNormalizer(),         # TTS post-step
]

class KhmerNormalizer:  
    def __init__(self, normalizers=None):
        self.normalizers = list(normalizers) if normalizers is not None else list(DEFAULT_PIPELINE)

    def normalize(self, text: str) -> str:
        # Text passes sequentially through every normalizer in the list
        for n in self.normalizers:
            text = n.normalize(text)
        return text


if __name__ == "__main__":
    # Initialize your orchestrator
    normalizer = KhmerNormalizer()
    
    # A raw sentence containing multiple entity types
    raw_text = "ប្រាក់ខែ 9492 dollars ហើយនេះជាមុខវិជ្ជាទី67 មានកម្ពស់ 571.7054 ម៉ែត្រ។"
    
    print("--- Running Sequential Cascade Pipeline ---")
    print(f"Raw Text:   {raw_text}")
    
    # Run the text through the pipeline
    final_text = normalizer.normalize(raw_text)
    
    print(f"Normalized: {final_text}")