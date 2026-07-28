#!/usr/bin/env python3
"""Bounded local regex builder and tester for archive metadata."""

import argparse
import json
import re
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and test a Python regex locally.")
    parser.add_argument("--literal", action="append", default=[])
    parser.add_argument("--character-class")
    parser.add_argument("--anchor-start", action="store_true")
    parser.add_argument("--anchor-end", action="store_true")
    parser.add_argument("--group")
    parser.add_argument("--alternate", action="append", default=[])
    parser.add_argument("--quantifier", choices=["?", "*", "+"])
    parser.add_argument("--pattern")
    parser.add_argument("--sample", default="")
    parser.add_argument("--flags", default="", help="Any of: i, m, s")
    args = parser.parse_args()
    if len(args.sample) > 100_000:
        parser.error("sample is limited to 100,000 characters")
    pattern = args.pattern
    if pattern is None:
        parts = [re.escape(value) for value in args.literal]
        if args.character_class:
            parts.append(f"[{args.character_class}]")
        if args.group:
            parts.append(f"({args.group})")
        if args.alternate:
            parts.append(f"(?:{'|'.join(args.alternate)})")
        pattern = "".join(parts)
        if args.quantifier:
            pattern = f"(?:{pattern}){args.quantifier}"
        pattern = ("^" if args.anchor_start else "") + pattern
        pattern += "$" if args.anchor_end else ""
    if len(pattern) > 4_096:
        parser.error("pattern is limited to 4,096 characters")
    flags = sum(
        value for key, value in {"i": re.I, "m": re.M, "s": re.S}.items() if key in args.flags
    )
    try:
        expression = re.compile(pattern, flags)
    except re.error as exc:
        print(json.dumps({"valid": False, "error": str(exc), "pattern": pattern}))
        return 2
    matches = []
    for index, match in enumerate(expression.finditer(args.sample)):
        if index >= 1_000:
            break
        matches.append({"span": match.span(), "text": match.group(), "groups": match.groups()})
    print(json.dumps({"valid": True, "pattern": pattern, "matches": matches}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
