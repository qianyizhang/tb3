#!/usr/bin/env python3
"""Portable records, source-linked measurements and exact scientific figures."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from tb3_medical.presentation import check
if __name__ == '__main__':
    print(json.dumps(check(Path(__file__).resolve().parents[1]), indent=2))
