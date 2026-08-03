#!/usr/bin/env python3
"""Print frontier ChartQA clean-source preference at every saved level."""

import argparse
import json
from collections import Counter
from pathlib import Path


def level_rows(model_dir):
    output = {}
    for path in model_dir.glob("level_*.generation.jsonl"):
        level = int(path.name.split("_", 2)[1])
        with path.open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
        output[level] = Counter(row.get("follows", "invalid") for row in rows)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--models", nargs="+", required=True)
    args = parser.parse_args()
    print("model\tarm\tlevel\tclean_source\tclean_preference\tdecidable\tneither\tinvalid")
    for model in args.models:
        for arm in ("image", "text"):
            for level, counts in sorted(level_rows(args.root / arm / model).items()):
                decidable = counts["image"] + counts["text"]
                if arm == "image":
                    clean_source = "text"
                    clean = counts["text"]
                else:
                    clean_source = "image"
                    clean = counts["image"]
                preference = clean / decidable if decidable else float("nan")
                print(f"{model}\t{arm}\tL{level}\t{clean_source}\t"
                      f"{preference:.4f}\t{decidable}\t{counts['neither']}\t"
                      f"{counts['invalid']}")


if __name__ == "__main__":
    main()
