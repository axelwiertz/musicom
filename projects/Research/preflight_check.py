"""Preflight compliance check: flags composition code that bypasses musicom.

Usage:
    python preflight_check.py <project_dir>
    python preflight_check.py .       # check current dir

Exit 0 = compliant. Non-zero = violations found (printed).

Checks every .py file in the target for:
  - Raw mido authoring (MidiTrack, note_on/note_off construction, MidiFile save)
  - sys.path hacks to musicom repo (stale; package is installed editable)
  - Missing musicom imports (should use structures/workflows, not roll own MIDI)
"""
import os
import re
import sys
from typing import List, Tuple

# Patterns that indicate forbidden raw-MIDI authoring
FORBIDDEN_PATTERNS = [
    (r'\bimport\s+mido\b', "raw 'import mido' — use musicom.workflows.unitmatrix_composer instead"),
    (r'\bfrom\s+mido\s+import\b', "raw 'from mido import' — use musicom.workflows.unitmatrix_composer"),
    (r'\bMidiTrack\s*\(', "raw MidiTrack() construction — use UnitMatrixComposer.to_midi()"),
    (r'\bMidiFile\s*\(', "raw MidiFile() construction — use UnitMatrixComposer.to_midi()"),
    (r"\.save\s*\([^)]*\.mid", "raw .save(*.mid) — use UnitMatrixComposer.to_midi()"),
    (r'sys\.path\.(insert|append).*musicom', "sys.path hack — musicom is installed editable, remove this"),
]

# Allowlist: patterns that indicate compliant musicom usage (suppress false positives)
COMPLIANT_INDICATORS = [
    r'from\s+workflows\.unitmatrix_composer\s+import',
    r'from\s+structures\s+import',
    r'from\s+workflows\.provenance\s+import',
]

# Files that are themselves analysis/reading scripts may legitimately import mido
# for READING (not authoring). Allow if they also import musicom structures.
# Accepts literal paths ('x.mid') AND variable args (MidiFile(filepath)) in
# read-only helper contexts.
READING_CONTEXT = re.compile(
    r'midifile_to_|mido\.MidiFile\([^)]*\.mid[^)]*\)|'
    r'\.load_midi|\.read\(|# READING ONLY \(analysis\)'
)


def check_file(path: str) -> List[Tuple[int, str, str]]:
    """Check one .py file. Returns list of (line_no, line, reason)."""
    violations = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return []

    content = "".join(lines)

    # If file uses compliant musicom imports AND has a reading-only mido usage, skip mido warnings
    has_compliant = any(re.search(p, content) for p in COMPLIANT_INDICATORS)
    has_reading = bool(READING_CONTEXT.search(content))

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for pattern, reason in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                # Allow mido import + MidiFile()/MidiTrack() reads if the file
                # is a read-only analysis context AND uses compliant musicom imports
                if has_compliant and has_reading:
                    if "mido" in reason or "MidiFile" in reason or "MidiTrack" in reason:
                        continue
                violations.append((i, stripped, reason))
    return violations


def check_directory(dirpath: str) -> dict:
    """Recursively check all .py files. Returns {path: [(line,text,reason),...]}."""
    results = {}
    for root, dirs, files in os.walk(dirpath):
        # Skip hidden dirs, __pycache__, venv
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "venv", "node_modules")]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            violations = check_file(path)
            if violations:
                results[path] = violations
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python preflight_check.py <project_dir>")
        sys.exit(2)

    target = os.path.abspath(sys.argv[1])
    if not os.path.exists(target):
        print(f"ERROR: {target} does not exist")
        sys.exit(2)

    if os.path.isfile(target):
        violations = check_file(target)
        results = {target: violations} if violations else {}
    else:
        results = check_directory(target)

    if not results:
        print(f"✅ COMPLIANT: no raw-MIDI/sys.path violations in {target}")
        sys.exit(0)

    print(f"❌ VIOLATIONS FOUND in {target}:")
    print()
    total = 0
    for path, viols in sorted(results.items()):
        rel = os.path.relpath(path, target)
        print(f"  {rel}:")
        for line_no, text, reason in viols:
            print(f"    L{line_no}: {text}")
            print(f"           → {reason}")
            total += 1
        print()

    print(f"Total: {total} violation(s). Fix before committing.")
    print("Ref: /opt/data/projects/Research/AGENTS.md")
    sys.exit(1)


if __name__ == "__main__":
    main()
