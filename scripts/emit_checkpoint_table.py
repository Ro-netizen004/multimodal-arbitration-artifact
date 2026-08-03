#!/usr/bin/env python3
"""Emit the checkpoint/revision rows printed as Table 2 in the paper."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "configs" / "model_revisions.json").read_text(encoding="utf-8"))
print("checkpoint\trevision")
for row in rows:
    print(f"{row['checkpoint']}\t{row['revision']}")
