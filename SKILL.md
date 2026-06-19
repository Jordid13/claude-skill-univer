---
name: sheet-edit
description: Edit Obsidian Univer spreadsheets (.univer.md files). Use when the user asks to read, write, clear, or interact with spreadsheet cells, when working with .univer.md files, or when operating inside an Obsidian vault that contains spreadsheets.
user-invocable: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py *)
arguments: [file]
---

## Overview

This skill provides a CLI tool for editing Obsidian Univer spreadsheets (`.univer.md` files) without reading the raw JSON directly. Always use the script instead of manually reading or editing `.univer.md` files.

## Commands

```bash
# Read a single cell
python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py <file> read <cell>

# Write a value to a cell
python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py <file> write <cell> <value>

# Read a range of cells (displayed as a table)
python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py <file> read-range <start>:<end>

# Clear a cell
python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py <file> clear <cell>

# List all sheets in the file
python3 ${CLAUDE_SKILL_DIR}/scripts/sheet_tool.py <file> sheets
```

### Optional flags

- `--sheet <name>` — target a specific sheet (defaults to first sheet)

## Cell references

Use A1-style references: `A1`, `B3`, `AA1`, etc. Column letters are case-insensitive.

## Type detection

The tool auto-detects value types:
- Numbers (`42`, `3.14`) are stored as numeric
- Formulas (`=SUM(A1:A3)`) are stored as formulas
- Everything else is stored as text

## Instructions

- If the user provides `$0` as a file argument, use that path. Otherwise, find the relevant `.univer.md` file in the working directory.
- Always use this script to interact with `.univer.md` files. Never read or edit the raw JSON manually.
- When writing multiple cells, batch them in a single Bash call using `&&` or a loop to reduce round trips.
- When the user asks to see spreadsheet contents, use `read-range` to show a meaningful range rather than reading individual cells.
