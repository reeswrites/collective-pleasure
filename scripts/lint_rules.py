"""Lint every rule set in rules/ (and a sample of negotiated agreements). Exit 1 if any set fails or is open without `known_flaw`.

  uv run python scripts/lint_rules.py                 # print the table, exit code 1 on failure
  uv run python scripts/lint_rules.py --detail        # every finding
  uv run python scripts/lint_rules.py --md docs/results/lint.md
"""
import argparse
import sys

from mar import lint as L


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=L.K_DEFAULT)
    ap.add_argument("--negotiated", type=int, default=40, help="sample size of compiled negotiated agreements (0 = none)")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--md", default=None, help="write the findings as a markdown table to this path")
    a = ap.parse_args(argv)
    res = L.lint_all(k=a.k, negotiated=a.negotiated)
    print(L.summary_table(res))
    if a.detail:
        for r in res:
            for f in r["findings"]:
                print(f"{r['name']}: {f['check']} {f['verdict']}{' (waived)' if f['waived'] else ''} {f['cards']}: {f['detail']}")
    if a.md:
        from pathlib import Path
        Path(a.md).write_text(L.markdown(res, a.k), encoding="utf-8")
    bad = [r for r in res if r["status"] != "pass"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
