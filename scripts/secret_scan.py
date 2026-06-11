#!/usr/bin/env python3
"""Lightweight repo secret scanner.
Scans staged files (or entire workspace) for common secret patterns.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    re.compile(r"claude", re.I),
    re.compile(r"api[_-]?key", re.I),
    re.compile(r"secret", re.I),
    re.compile(r"aws[_-]?access[_-]?key", re.I),
    re.compile(r"aws[_-]?secret[_-]?access[_-]?key", re.I),
    re.compile(r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----"),
]

def scan_file(path: Path):
    try:
        text = path.read_text(errors='ignore')
    except Exception:
        return []
    hits = []
    for i,line in enumerate(text.splitlines(), start=1):
        for p in PATTERNS:
            if p.search(line):
                hits.append((i, line.strip()))
                break
    return hits

def main():
    # if files provided, scan those, else scan all non-binary files under repo
    paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else [p for p in ROOT.rglob('*') if p.is_file()]
    findings = {}
    for p in paths:
        # skip git dir
        if '.git' in p.parts:
            continue
        if p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.pb', '.zip', '.tar', '.gz']:
            continue
        hits = scan_file(p)
        if hits:
            findings[str(p.relative_to(ROOT))] = hits

    if not findings:
        print('No likely secrets found.')
        return 0

    print('Potential secrets found:')
    for f,hits in findings.items():
        print(f"\nIn {f}:")
        for lineno, line in hits:
            print(f"  {lineno}: {line}")
    return 2

if __name__ == '__main__':
    sys.exit(main())
