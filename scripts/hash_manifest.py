#!/usr/bin/env python3
"""Source manifests for local/StudioNet parity; prints, never asserts live proof."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=['contracts/courselock.py','contracts/course_consumer.py','package.json',
       'gltest.config.yaml','scripts/assert_studionet.mjs','scripts/deploy_studionet.mjs']
rows={}
for f in files:
    rows[f]=hashlib.sha256((root/f).read_bytes()).hexdigest()
print(json.dumps(rows,sort_keys=True,indent=2))
