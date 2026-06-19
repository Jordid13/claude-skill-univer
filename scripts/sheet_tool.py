#!/usr/bin/env python3
"""CLI tool for reading and editing Obsidian Univer spreadsheets (.univer.md files)."""

import json
import re
import sys


def parse_cell_ref(ref):
    """Convert A1-style cell reference to zero-based (row, col) tuple."""
    match = re.match(r'^([A-Za-z]+)(\d+)$', ref)
    if not match:
        print(f"Error: Invalid cell reference '{ref}'. Use A1-style (e.g., A1, B3, AA1).", file=sys.stderr)
        sys.exit(1)
    col_str = match.group(1).upper()
    row = int(match.group(2)) - 1
    col = 0
    for ch in col_str:
        col = col * 26 + (ord(ch) - ord('A') + 1)
    col -= 1
    return row, col


def col_to_letter(col):
    """Convert zero-based column index to letter(s) (0=A, 25=Z, 26=AA)."""
    result = []
    col += 1
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result.append(chr(ord('A') + remainder))
    return ''.join(reversed(result))


def parse_file(filepath):
    """Parse a .univer.md file into its components."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    fm_match = re.match(r'^(---\n.*?\n---\n)', content, re.DOTALL)
    if not fm_match:
        print("Error: Could not find YAML frontmatter.", file=sys.stderr)
        sys.exit(1)
    frontmatter = fm_match.group(1)
    rest = content[fm_match.end():]

    # Extract ```sheet block
    sheet_match = re.search(r'```sheet\n(.*?)\n```', rest, re.DOTALL)
    if not sheet_match:
        print("Error: Could not find ```sheet code block.", file=sys.stderr)
        sys.exit(1)
    sheet_json = json.loads(sheet_match.group(1))

    # Extract ```multiSheet block (preserve as-is)
    multi_match = re.search(r'(```multiSheet\n.*?\n```)', rest, re.DOTALL)
    multi_block = multi_match.group(1) if multi_match else None

    return frontmatter, sheet_json, multi_block


def write_file(filepath, frontmatter, sheet_json, multi_block):
    """Reassemble and write the .univer.md file."""
    parts = [frontmatter]
    parts.append('```sheet\n')
    parts.append(json.dumps(sheet_json, ensure_ascii=False, separators=(',', ':')))
    parts.append('\n```\n')
    if multi_block:
        parts.append('\n' + multi_block + '\n')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))


def get_sheet(sheet_json, sheet_name=None):
    """Get a sheet by name or the first sheet if no name given."""
    sheets = sheet_json.get('sheets', {})
    if not sheets:
        print("Error: No sheets found in file.", file=sys.stderr)
        sys.exit(1)

    if sheet_name:
        for sid, sheet in sheets.items():
            if sheet.get('name') == sheet_name:
                return sid, sheet
        print(f"Error: Sheet '{sheet_name}' not found. Available: {', '.join(s.get('name', sid) for sid, s in sheets.items())}", file=sys.stderr)
        sys.exit(1)

    # Use sheetOrder if available, otherwise first sheet
    order = sheet_json.get('sheetOrder', [])
    if order:
        sid = order[0]
        return sid, sheets[sid]
    sid = next(iter(sheets))
    return sid, sheets[sid]


def detect_type(value):
    """Auto-detect cell type from string value. Returns (v, t) or (v, t, f) for formulas."""
    if value.startswith('='):
        return {'f': value, 't': 1, 'v': None}
    try:
        num = int(value)
        return {'v': num, 't': 2}
    except ValueError:
        pass
    try:
        num = float(value)
        return {'v': num, 't': 2}
    except ValueError:
        pass
    return {'v': value, 't': 1}


def cmd_read(filepath, cell_ref, sheet_name=None):
    """Read a single cell value."""
    _, sheet_json, _ = parse_file(filepath)
    _, sheet = get_sheet(sheet_json, sheet_name)
    row, col = parse_cell_ref(cell_ref)
    cell_data = sheet.get('cellData', {})
    row_data = cell_data.get(str(row), {})
    cell = row_data.get(str(col))
    if cell is None:
        print("")
    else:
        val = cell.get('f') or cell.get('v', '')
        print(val)


def cmd_write(filepath, cell_ref, value, sheet_name=None):
    """Write a value to a single cell."""
    frontmatter, sheet_json, multi_block = parse_file(filepath)
    sid, sheet = get_sheet(sheet_json, sheet_name)
    row, col = parse_cell_ref(cell_ref)
    cell_data = sheet.setdefault('cellData', {})
    row_data = cell_data.setdefault(str(row), {})
    row_data[str(col)] = detect_type(value)
    sheet_json['sheets'][sid] = sheet
    write_file(filepath, frontmatter, sheet_json, multi_block)
    print(f"Wrote '{value}' to {cell_ref}")


def cmd_read_range(filepath, range_ref, sheet_name=None):
    """Read a range of cells and display as a table."""
    parts = range_ref.split(':')
    if len(parts) != 2:
        print("Error: Range must be in format A1:C3", file=sys.stderr)
        sys.exit(1)
    start_row, start_col = parse_cell_ref(parts[0])
    end_row, end_col = parse_cell_ref(parts[1])

    _, sheet_json, _ = parse_file(filepath)
    _, sheet = get_sheet(sheet_json, sheet_name)
    cell_data = sheet.get('cellData', {})

    # Build header
    headers = [''] + [col_to_letter(c) for c in range(start_col, end_col + 1)]
    rows = []
    for r in range(start_row, end_row + 1):
        row_vals = [str(r + 1)]
        for c in range(start_col, end_col + 1):
            cell = cell_data.get(str(r), {}).get(str(c))
            if cell is None:
                row_vals.append('')
            else:
                row_vals.append(str(cell.get('f') or cell.get('v', '')))
        rows.append(row_vals)

    # Calculate column widths
    all_rows = [headers] + rows
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(headers))]

    # Print table
    for row in all_rows:
        print('  '.join(val.ljust(widths[i]) for i, val in enumerate(row)))


def cmd_clear(filepath, cell_ref, sheet_name=None):
    """Clear a cell."""
    frontmatter, sheet_json, multi_block = parse_file(filepath)
    sid, sheet = get_sheet(sheet_json, sheet_name)
    row, col = parse_cell_ref(cell_ref)
    cell_data = sheet.get('cellData', {})
    row_data = cell_data.get(str(row), {})
    if str(col) in row_data:
        del row_data[str(col)]
        if not row_data:
            del cell_data[str(row)]
        sheet_json['sheets'][sid] = sheet
        write_file(filepath, frontmatter, sheet_json, multi_block)
    print(f"Cleared {cell_ref}")


def cmd_sheets(filepath):
    """List all sheets in the file."""
    _, sheet_json, _ = parse_file(filepath)
    sheets = sheet_json.get('sheets', {})
    order = sheet_json.get('sheetOrder', list(sheets.keys()))
    for i, sid in enumerate(order):
        sheet = sheets.get(sid, {})
        name = sheet.get('name', sid)
        rows = sheet.get('rowCount', '?')
        cols = sheet.get('columnCount', '?')
        print(f"  {i+1}. {name} ({rows} rows x {cols} cols)")


def main():
    if len(sys.argv) < 3:
        print("Usage: sheet_tool.py <file> <command> [args...] [--sheet <name>]")
        print()
        print("Commands:")
        print("  read <cell>            Read a cell value")
        print("  write <cell> <value>   Write a value to a cell")
        print("  read-range <A1:C3>     Read a range of cells")
        print("  clear <cell>           Clear a cell")
        print("  sheets                 List all sheets")
        sys.exit(1)

    filepath = sys.argv[1]
    command = sys.argv[2]

    # Parse optional --sheet flag
    sheet_name = None
    args = sys.argv[3:]
    if '--sheet' in args:
        idx = args.index('--sheet')
        if idx + 1 < len(args):
            sheet_name = args[idx + 1]
            args = args[:idx] + args[idx+2:]
        else:
            print("Error: --sheet requires a name", file=sys.stderr)
            sys.exit(1)

    if command == 'read':
        if len(args) < 1:
            print("Usage: sheet_tool.py <file> read <cell>", file=sys.stderr)
            sys.exit(1)
        cmd_read(filepath, args[0], sheet_name)
    elif command == 'write':
        if len(args) < 2:
            print("Usage: sheet_tool.py <file> write <cell> <value>", file=sys.stderr)
            sys.exit(1)
        cmd_write(filepath, args[0], ' '.join(args[1:]), sheet_name)
    elif command == 'read-range':
        if len(args) < 1:
            print("Usage: sheet_tool.py <file> read-range <A1:C3>", file=sys.stderr)
            sys.exit(1)
        cmd_read_range(filepath, args[0], sheet_name)
    elif command == 'clear':
        if len(args) < 1:
            print("Usage: sheet_tool.py <file> clear <cell>", file=sys.stderr)
            sys.exit(1)
        cmd_clear(filepath, args[0], sheet_name)
    elif command == 'sheets':
        cmd_sheets(filepath)
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
