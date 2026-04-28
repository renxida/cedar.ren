#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Validate data.yml positions against the actual ZMK keymap.

For each row that declares `layer` + `binding` + diagram positions, look up
the binding in the parsed keymap and report mismatches.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).parent
KEYMAP = Path("/Users/cedar/playground/zmk-config/config/base.keymap")

L_LAYOUT = [['Q','W','F','P','B'],['A','R','S','T','G'],['Z','X','C','D','V']]
R_LAYOUT = [['J','L','U','Y',"'"],['M','N','E','I','O'],['K','H',',','.','?']]

# How many tokens after `&macro` to consume.
ARG_COUNTS = {
    '___': 0, '&trans': 0, '&none': 0,
    '&bootloader': 0, '&sys_reset': 0,
    '&kp': 1, '&mo': 1, '&to': 1, '&tog': 1, '&sl': 1, '&sk': 1,
    '&out': 1, '&mkp': 1,
    '&hml': 2, '&hmr': 2, '&mt': 2, '&lt': 2, '&lt_spc': 2, '&lt_num': 2,
    '&bt': 2,   # &bt BT_SEL N  or  &bt BT_CLR  — handle BT_CLR as 1-arg below
    '&smart_num': 0, '&smart_shift': 0,
    'MAGIC_SHIFT': 0, 'SMART_NUM': 0,
    'U_MS_U': 0, 'U_MS_L': 0, 'U_MS_D': 0, 'U_MS_R': 0,
    'U_WH_U': 0, 'U_WH_L': 0, 'U_WH_D': 0, 'U_WH_R': 0,
}

# Expansion of compound macros into 5 bindings (top-left row only).
MACRO_EXPANSIONS = {
    '_BT_SEL_KEYS_': ['&bt BT_SEL 0', '&bt BT_SEL 1', '&bt BT_SEL 2', '&bt BT_SEL 3', '&bt BT_CLR'],
}


def parse_bindings(field: str, expected_n: int) -> list[str]:
    """Parse a comma-delimited field into N bindings."""
    field = field.strip()
    if not field:
        return ['___'] * expected_n
    # Macro expansion (must appear alone in the field)
    if field in MACRO_EXPANSIONS:
        return MACRO_EXPANSIONS[field]
    tokens = field.split()
    bindings = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == '___':
            bindings.append('___')
            i += 1
        elif t in ARG_COUNTS:
            n = ARG_COUNTS[t]
            # Special-case &bt BT_CLR (1-arg)
            if t == '&bt' and i+1 < len(tokens) and tokens[i+1] == 'BT_CLR':
                n = 1
            args = tokens[i+1 : i+1+n]
            bindings.append(' '.join([t] + args))
            i += 1 + n
        else:
            # Unknown — treat as single binding (e.g. user macro)
            bindings.append(t)
            i += 1
    if len(bindings) != expected_n:
        # Try interpreting unknown tokens as 0-arg bindings (already done)
        # If still mismatched, return what we got and let validator note it
        pass
    return bindings


def parse_keymap(text: str) -> dict[str, dict[tuple, str]]:
    """Return {layer_name: {(side, row, col): binding_string}}.

    Side is 'L' or 'R'. Row 0..2 for the 3-row grid, or 'TH' for thumbs (col 0..1).
    """
    layers = {}
    # Anchor at start of line to skip the `#define ZMK_BASE_LAYER(...)` macro definition.
    pattern = re.compile(r'^ZMK_BASE_LAYER\(\s*(\w+)\s*,\s*(.*?)\n\)', re.DOTALL | re.MULTILINE)
    for m in pattern.finditer(text):
        name = m.group(1)
        body = m.group(2)
        # Strip line comments
        body_lines = []
        for line in body.splitlines():
            line = re.sub(r'//.*$', '', line)
            body_lines.append(line)
        body_clean = ' '.join(body_lines)
        # Split on commas — should yield 8 fields: 3 row pairs (L, R), then (LH, RH)
        fields = [f.strip() for f in body_clean.split(',')]
        # Filter trailing empties (a final comma is allowed)
        while fields and fields[-1] == '':
            fields.pop()
        if len(fields) < 8:
            print(f"  warn: layer {name} has {len(fields)} fields, expected 8")
            continue
        positions = {}
        # Rows
        for r in range(3):
            left_field = fields[2*r]
            right_field = fields[2*r + 1]
            lb = parse_bindings(left_field, 5)
            rb = parse_bindings(right_field, 5)
            for c in range(min(5, len(lb))):
                positions[('L', r, c)] = lb[c]
            for c in range(min(5, len(rb))):
                positions[('R', r, c)] = rb[c]
        # Thumbs (2 each)
        l_thumbs = parse_bindings(fields[6], 2)
        r_thumbs = parse_bindings(fields[7], 2)
        # By Cradio convention: left field is [LO, LI], right is [RI, RO]
        if len(l_thumbs) >= 2:
            positions[('TH', 'LO')] = l_thumbs[0]
            positions[('TH', 'LI')] = l_thumbs[1]
        if len(r_thumbs) >= 2:
            positions[('TH', 'RI')] = r_thumbs[0]
            positions[('TH', 'RO')] = r_thumbs[1]
        layers[name] = positions
    return layers


def find_letter(letter: str, layout) -> tuple[int, int] | None:
    for r, row in enumerate(layout):
        for c, k in enumerate(row):
            if k == letter:
                return r, c
    return None


def validate(data: dict, layers: dict) -> int:
    """Return number of issues found."""
    issues = 0
    checked = 0
    for sec in data.get('sections', []):
        for row in sec.get('rows', []):
            layer = row.get('layer')
            binding = row.get('binding')
            if not layer or not binding:
                continue
            if layer not in layers:
                print(f"  ! [{sec['name']}] '{row['action']}': layer '{layer}' not found in keymap")
                issues += 1
                continue
            positions = layers[layer]
            # Walk through keys[].diagram
            for item in row.get('keys', []) or []:
                if not isinstance(item, dict):
                    continue
                diag = item.get('diagram') or item.get('inline_diagram')
                if not diag:
                    continue
                for letter in diag.get('left', []) or []:
                    rc = find_letter(str(letter).upper() if str(letter).isalpha() else str(letter), L_LAYOUT)
                    if rc is None:
                        continue
                    r, c = rc
                    actual = positions.get(('L', r, c), '?')
                    checked += 1
                    if not _matches(binding, actual):
                        print(f"  ! [{layer}] L:{letter} expected '{binding}', keymap has '{actual}'  ({row['action']})")
                        issues += 1
                for letter in diag.get('right', []) or []:
                    rc = find_letter(str(letter).upper() if str(letter).isalpha() else str(letter), R_LAYOUT)
                    if rc is None:
                        continue
                    r, c = rc
                    actual = positions.get(('R', r, c), '?')
                    checked += 1
                    if not _matches(binding, actual):
                        print(f"  ! [{layer}] R:{letter} expected '{binding}', keymap has '{actual}'  ({row['action']})")
                        issues += 1
                for thumb in diag.get('thumbs', []) or []:
                    actual = positions.get(('TH', thumb), '?')
                    checked += 1
                    if not _matches(binding, actual):
                        print(f"  ! [{layer}] T:{thumb} expected '{binding}', keymap has '{actual}'  ({row['action']})")
                        issues += 1
    print(f"\nchecked {checked} positions, {issues} issue(s)")
    return issues


def _matches(expected: str, actual: str) -> bool:
    """Soft match — allow wildcards and prefix matches.

    Examples:
      expected '&bt BT_SEL'    matches '&bt BT_SEL 0'
      expected '&kp PG_*'      matches '&kp PG_UP'
      expected 'U_MS_*'        matches 'U_MS_U'
      expected '&sys_reset'    matches exactly
    """
    if expected == actual:
        return True
    if '*' in expected:
        prefix = expected.split('*')[0]
        return actual.startswith(prefix)
    # treat expected as prefix-match if it has no args but actual does
    if actual.startswith(expected + ' '):
        return True
    return False


def main():
    if not KEYMAP.exists():
        print(f"keymap not found at {KEYMAP}")
        sys.exit(2)
    data = yaml.safe_load((ROOT / 'data.yml').read_text())
    layers = parse_keymap(KEYMAP.read_text())
    print(f"parsed layers: {list(layers.keys())}")
    issues = validate(data, layers)
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
