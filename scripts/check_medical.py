#!/usr/bin/env python3
"""Portable records, source-linked measurements and exact scientific figures."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from tb3_medical.presentation import check
from tb3_medical.task_briefs import check as check_briefs
if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print(json.dumps({**check(root), "task_briefs": check_briefs(root)}, indent=2))
