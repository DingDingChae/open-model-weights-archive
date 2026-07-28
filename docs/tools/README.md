# Tools

## Regex builder

`scripts/regex-builder.py` provides guided literals, character classes,
anchors, groups, alternation, quantifiers, a raw pattern editor, `i/m/s` flags,
syntax feedback, bounded sample input, live matches, and capture groups using
Python's `re` engine.

```powershell
python scripts/regex-builder.py --literal qwen --alternate deepseek `
  --sample "qwen deepseek"
```

Evaluation is local. Patterns are limited to 4,096 characters, samples to
100,000 characters, and output to 1,000 matches.
