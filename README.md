# Claude Skill: Univer Spreadsheet Editor

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for reading, writing, and formatting [Obsidian Univer](https://github.com/dream-num/obsidian-univer) spreadsheets (`.univer.md` files) from the command line.

## Installation

Add the skill to your Claude Code project:

```bash
claude skill add /path/to/sheet-edit
```

Or clone this repo into your skills directory:

```bash
git clone git@github.com:Jordid13/claude-skill-univer.git ~/.claude/skills/sheet-edit
```

## Requirements

- Python 3.6+
- No external dependencies

## Commands

### Data

| Command | Usage | Description |
|---------|-------|-------------|
| `read` | `read <cell>` | Read a single cell value |
| `write` | `write <cell> <value>` | Write a value to a cell |
| `read-range` | `read-range <start>:<end>` | Read a range as a table |
| `clear` | `clear <cell>` | Clear a cell |
| `sheets` | `sheets` | List all sheets in the file |

### Formatting

| Command | Usage | Description |
|---------|-------|-------------|
| `auto-fit` | `auto-fit` | Auto-fit column widths to content |
| `set-col-width` | `set-col-width <col> <px>` | Set a column's width in pixels |
| `freeze` | `freeze <rows>` | Freeze top N rows (0 to unfreeze) |
| `bg-color` | `bg-color <cell\|range> <hex>` | Set background color |
| `text-color` | `text-color <cell\|range> <hex>` | Set text color |
| `border` | `border <cell\|range> <hex> [style] [sides]` | Set borders |

### Border options

**Styles:** `none`, `thin`, `hair`, `dotted`, `dashed`, `dash-dot`, `dash-dot-dot`, `double`, `medium`, `medium-dashed`, `medium-dash-dot`, `medium-dash-dot-dot`, `slant-dash-dot`, `thick`

**Sides:** `all`, `top`, `bottom`, `left`, `right`, `outer`

## Usage examples

```bash
TOOL="python3 scripts/sheet_tool.py"
FILE="my_spreadsheet.univer.md"

# Write data
$TOOL "$FILE" write A1 "Name"
$TOOL "$FILE" write B1 "Score"
$TOOL "$FILE" write A2 "Alice"
$TOOL "$FILE" write B2 95

# Read it back
$TOOL "$FILE" read-range A1:B2

# Format it
$TOOL "$FILE" auto-fit
$TOOL "$FILE" freeze 1
$TOOL "$FILE" bg-color A1:B1 "#2563eb"
$TOOL "$FILE" text-color A1:B1 "#ffffff"
$TOOL "$FILE" border A1:B1 "#000000" thick bottom
```

### Optional flags

- `--sheet <name>` — target a specific sheet (defaults to first sheet)

## Cell references

Use A1-style references: `A1`, `B3`, `AA1`, etc. Column letters are case-insensitive. Ranges use colon notation: `A1:J1`.

## Type detection

Values are auto-detected:
- Numbers (`42`, `3.14`) are stored as numeric
- Formulas (`=SUM(A1:A3)`) are stored as formulas
- Everything else is stored as text

## Roadmap

Features not yet supported but planned for the future:

- **Bold / Italic / Underline / Strikethrough** — cell text styling
- **Font family and size** — changing fonts per cell or range
- **Text alignment** — horizontal (left, center, right) and vertical alignment
- **Number formatting** — currency, percentages, date formats, custom patterns
- **Merge cells** — merging and unmerging cell ranges
- **Row height** — setting row heights manually or auto-fitting
- **Conditional formatting** — color scales, data bars, icon sets
- **Data validation** — dropdowns, input restrictions
- **Named ranges** — defining and referencing named ranges
- **Multi-sheet operations** — copying/moving data across sheets, add/delete sheets
- **Bulk write** — writing multiple cells in a single command (e.g., from CSV)
- **Undo / History** — tracking and reverting changes

## License

MIT
