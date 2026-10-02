#!/usr/bin/env python3
"""Refresh one note's README metadata from hash-checked measurement history."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = {"001": "001-nem-duration-baseline", "004": "004-gb-duration-baseline"}


def refresh(root, note):
    folder = root / "notes" / NOTES[note]
    history = json.loads((folder / "history/measurement_log.json").read_text())
    entry = history[-1]
    digest = hashlib.sha256((folder / "results.json").read_bytes()).hexdigest()
    if digest != entry["results_sha256"]:
        raise ValueError("Results hash differs from latest measurement history")
    window = entry["measurement_window"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}", window):
        raise ValueError("Invalid measurement window")
    path = root / "README.md"
    content = path.read_text()
    pattern = rf"(?m)^(\| `OMN-{note}` \|[^\n]+)$"
    rows = list(re.finditer(pattern, content))
    if len(rows) != 1:
        raise ValueError("Expected exactly one registry row")
    cells = rows[0].group().split("|")
    cells[4] = f" `{digest[:12]}...` "
    content = content[:rows[0].start()] + "|".join(cells) + content[rows[0].end():]
    pattern = rf"(?ms)(^\d+\. \*\*\[Note #{note}:.*?)(?=^\d+\. \*\*\[Note #|^---)"
    matches = list(re.finditer(pattern, content))
    if len(matches) != 1:
        raise ValueError("Expected exactly one active note section")
    section = matches[0].group()
    section, count = re.subn(r"(?m)(^   \* \*Scope:\* .*?) from .*\.$", rf"\g<1> from {window}.", section)
    if count != 1:
        raise ValueError("Expected exactly one scope line")
    status = f"   * *Status:* Latest measurement `{entry['version']}` (executed at `{entry['executed_at']}`; see [measurement history](./notes/{NOTES[note]}/history/measurement_log.json))."
    section, count = re.subn(r"(?m)^   \* \*Status:\* .*?$", lambda _: status, section)
    if count != 1:
        raise ValueError("Expected exactly one status line")
    content = content[:matches[0].start()] + section + content[matches[0].end():]
    path.write_text(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--note-id", required=True, choices=NOTES)
    args = parser.parse_args()
    refresh(ROOT, args.note_id)
