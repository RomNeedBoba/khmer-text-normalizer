import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from khmer_tn import KhmerNormalizer
from khmer_tn.categories import PauseNormalizer
from khmer_tn.clean import Cleaner
from khmer_tn.segment import Segmenter

n = KhmerNormalizer(pause=PauseNormalizer(mode="preserve"))

CASES = [
    # (input, must_contain, must_not_contain)
    ("ទូរស័ព្ទ 012 345 678", ["សូន្យ មួយ ពីរ បី បួន ប្រាំ ប្រាំមួយ ប្រាំពីរ ប្រាំបី"], ["012"]),
    ("+855 12 345 678", ["បូក ប្រាំបី ប្រាំ ប្រាំ"], ["855"]),
    # cascade bug 1: ordinal must not eat the date's day
    ("ថ្ងៃទី 15/07/2026", ["ថ្ងៃទីដប់ប្រាំ", "ខែកក្កដា", "ឆ្នាំពីរពាន់ម្ភៃប្រាំមួយ"], ["/", "15"]),
    ("2026-07-15", ["ថ្ងៃទីដប់ប្រាំ", "ខែកក្កដា"], ["-"]),
    # cascade bug 2: decimal must not eat money's amount
    ("$25.50", ["ម្ភៃប្រាំដុល្លារ", "ហាសិបសេន"], ["$", "ក្បៀស"]),
    ("5000៛", ["ប្រាំពាន់រៀល"], ["៛"]),
    ("ម៉ោង 9:30", ["ម៉ោងប្រាំបួន", "សាមសិបនាទី"], [":"]),
    ("50% បាន", ["ហាសិបភាគរយ"], ["%"]),
    ("10km", ["ដប់គីឡូម៉ែត្រ"], ["km"]),
    ("ពី 2020-2026", ["ពីរពាន់ម្ភៃដល់ពីរពាន់ម្ភៃប្រាំមួយ"], ["-"]),
    ("ចំនួន ១២៣ នាក់", ["មួយរយម្ភៃបី"], ["១២៣"]),
    ("មុខវិជ្ជាទី3", ["ទីបី"], ["3"]),
    ("3/4 នៃចំណែក", ["បីភាគបួន"], ["/"]),
    ("support@example.com", ["អាត់", "ចុច"], ["@"]),
    # date must beat fraction on d/m/y
    ("14/02/2025", ["ថ្ងៃទីដប់បួន", "ខែកុម្ភៈ"], ["ភាគ"]),
]

def run():
    failed = 0
    for text, must, must_not in CASES:
        out = n.normalize(text)
        errs = [f"missing {m!r}" for m in must if m not in out]
        errs += [f"unexpected {m!r}" for m in must_not if m in out]
        status = "PASS" if not errs else "FAIL"
        if errs: failed += 1
        print(f"[{status}] {text!r} -> {out!r}" + (f"   {errs}" if errs else ""))

    # clean stage
    c = Cleaner()
    assert c("\u200bក\u200bខ  គ\u00a0!!??") == "កខ គ !?", c("\u200bក\u200bខ  គ\u00a0!!??")
    assert c("កាាាត់") == "កាត់"
    print("[PASS] cleaner")

    # segment stage (regex fallback)
    s = Segmenter(backend="regex")
    assert s('ម្ភៃប្រាំដុល្លារ <break time="500ms"/> hello') == 'ម្ភៃប្រាំដុល្លារ <break time="500ms"/> hello'
    print(f"[PASS] segmenter backend={Segmenter().backend}")

    # ssml pause via default pipeline
    full = KhmerNormalizer()
    out = full.normalize("តម្លៃ $25.50។ សូមទូរស័ព្ទ 012 345 678!")
    assert '<break time="500ms"/>' in out, out
    print(f"[PASS] ssml: {out!r}")

    print(f"\n{len(CASES)-failed}/{len(CASES)} span cases passed")
    return failed

FAILED = run()

# --- fix verification (run standalone additions) ---
from khmer_tn import KhmerNormalizer as KN
from khmer_tn.categories import PauseNormalizer as PN, TimeNormalizer

np = KN(pause=PN(mode="preserve"))
out = np.normalize("មានផ្លែឈើផ្សេងៗ")
assert "ផ្សេង ផ្សេង" in out and "ៗ" not in out, out
print(f"[PASS] repeat: {out!r}")

t = TimeNormalizer(period=True)
assert t.normalize("15:30") == "ម៉ោងបី សាមសិបនាទីរសៀល", t.normalize("15:30")
assert t.normalize("9:00") == "ម៉ោងប្រាំបួនព្រឹក", t.normalize("9:00")
assert t.normalize("20:15") == "ម៉ោងប្រាំបី ដប់ប្រាំនាទីយប់", t.normalize("20:15")
print("[PASS] time periods")

no = KN(pause=PN(mode="preserve"), decimal_convention="official")
out = no.normalize("តម្លៃ 2,5 គិតជាភាគរយ")
assert "ពីរក្បៀសប្រាំ" in out, out
print(f"[PASS] official decimal: {out!r}")

sys.exit(FAILED)
