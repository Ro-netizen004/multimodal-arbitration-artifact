#!/usr/bin/env python3
"""Rescore saved ChartQA generations with the canonical exact matcher."""

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.chartqa_attribution import classify, extract_final_answer, normalize_answer


def load_manifest(path: Path):
    if path.is_dir():
        from datasets import load_from_disk
        rows = load_from_disk(str(path))
    else:
        with path.open(encoding="utf-8") as handle:
            rows = ([json.loads(line) for line in handle if line.strip()]
                    if path.suffix == ".jsonl" else json.load(handle))
    return {
        int(row["conflict_id"]): {
            "image_answer": str(row.get("image_answer", row.get("chart_answer"))),
            "text_answer": str(row.get("text_answer", row.get("report_answer"))),
            "unit_class": row.get("unit_class", ""),
        }
        for row in rows
    }


def rescore_file(source: Path, destination: Path, manifest):
    output = []
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            result = json.loads(line)
            item = int(result["i"])
            if item not in manifest:
                raise RuntimeError(f"No manifest row for item {item} in {source}")
            follows, extracted, normalized = classify(
                result.get("prediction", ""), manifest[item]
            )
            result.update(extracted_final=extracted,
                          normalized_final=repr(normalized), follows=follows)
            output.append(result)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for result in output:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
    return output


def rescore_decodability_file(source: Path, destination: Path, manifest):
    output = []
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            result = json.loads(line)
            item = int(result["i"])
            if item not in manifest:
                raise RuntimeError(f"No manifest row for item {item} in {source}")
            unit = manifest[item].get("unit_class", "")
            extracted = extract_final_answer(
                result.get("prediction", ""), unit, prefer_leading=True
            )
            normalized = normalize_answer(extracted, unit)
            target = normalize_answer(str(result.get("target_answer", "")), unit)
            result.update(
                extracted_final=extracted,
                normalized_final=repr(normalized),
                correct=normalized is not None and normalized == target,
            )
            output.append(result)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for result in output:
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--models", nargs="+", required=True)
    args = parser.parse_args()
    if args.root.resolve() == args.output_root.resolve():
        raise SystemExit("--output-root must differ from --root")
    manifest = load_manifest(args.manifest)

    for arm in ("image", "text"):
        for model in args.models:
            source_dir = args.root / "evidence" / arm / model
            output_dir = args.output_root / "evidence" / arm / model
            if not source_dir.exists():
                print(f"SKIP missing {source_dir}")
                continue
            output_dir.mkdir(parents=True, exist_ok=True)
            for metadata in source_dir.glob("*.json"):
                if not metadata.name.startswith("summary_"):
                    shutil.copy2(metadata, output_dir / metadata.name)
            for cll_file in source_dir.glob("level_*.cll.jsonl"):
                shutil.copy2(cll_file, output_dir / cll_file.name)

            levels = {}
            for source in sorted(source_dir.glob("level_*.generation.jsonl")):
                rows = rescore_file(source, output_dir / source.name, manifest)
                level = int(source.name.split("_", 2)[1])
                counts = Counter(row["follows"] for row in rows)
                decidable = counts["image"] + counts["text"]
                levels[str(level)] = {
                    "n": len(rows), "counts": dict(counts),
                    "text_preference": (counts["text"] / decidable
                                        if decidable else None),
                }
                print(f"{model} {arm} L{level}: n={len(rows)} counts={dict(counts)}")
            if levels:
                summary = {"arm": arm, "mode": "generation", "levels": levels,
                           "rescored_from": str(args.root)}
                with (output_dir / "summary_generation.json").open(
                        "w", encoding="utf-8") as handle:
                    json.dump(summary, handle, indent=2)

            decodability_levels = {}
            for source in sorted(source_dir.glob("level_*.decodability.jsonl")):
                rows = rescore_decodability_file(
                    source, output_dir / source.name, manifest
                )
                level = int(source.name.split("_", 2)[1])
                correct = sum(bool(row.get("correct")) for row in rows)
                decodability_levels[str(level)] = {
                    "n": len(rows), "correct": correct,
                    "accuracy": correct / len(rows) if rows else None,
                    "errors": sum("error" in row for row in rows),
                }
                print(f"{model} {arm} L{level}: n={len(rows)} correct={correct} "
                      f"accuracy={correct / len(rows):.4f}")
            if decodability_levels:
                summary = {
                    "arm": arm, "mode": "decodability",
                    "levels": decodability_levels,
                    "rescored_from": str(args.root),
                }
                with (output_dir / "summary_decodability.json").open(
                        "w", encoding="utf-8") as handle:
                    json.dump(summary, handle, indent=2)


if __name__ == "__main__":
    main()
