from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "source-pack" / "diego"
OUTPUT = ROOT / "research" / "evidence" / "diego-workbook-profile.json"


def normalize(value):
    if value is None:
        return ""
    return str(value).strip()


def row_values(sheet, row_number: int):
    return [normalize(sheet.cell(row_number, column).value) for column in range(1, sheet.max_column + 1)]


def find_header_row(sheet) -> int:
    best_row = 1
    best_score = -1
    for row in range(1, min(sheet.max_row, 20) + 1):
        values = row_values(sheet, row)
        text_count = sum(bool(value) for value in values)
        signal_count = sum(
            any(token in value.lower() for token in ("name", "url", "email", "company", "position", "industry", "use case", "owner", "message", "match"))
            for value in values
        )
        score = text_count + (signal_count * 4)
        if score > best_score:
            best_row = row
            best_score = score
    return best_row


def safe_top_values(values, header: str):
    header_lower = header.lower()
    sensitive = any(token in header_lower for token in ("name", "email", "url", "linkedin", "message", "phone"))
    nonempty = [value for value in values if value]
    if sensitive:
        return {"nonempty": len(nonempty), "unique": len(set(nonempty)), "values_redacted": True}
    counts = Counter(nonempty)
    return {
        "nonempty": len(nonempty),
        "unique": len(counts),
        "top_values": counts.most_common(12),
    }


def profile_sheet(sheet):
    header_row = find_header_row(sheet)
    headers = row_values(sheet, header_row)
    while headers and not headers[-1]:
        headers.pop()
    data_rows = []
    for row in range(header_row + 1, sheet.max_row + 1):
        values = row_values(sheet, row)[: len(headers)]
        if any(values):
            data_rows.append(values)
    columns = {}
    for index, header in enumerate(headers):
        label = header or f"Column {index + 1}"
        columns[label] = safe_top_values([row[index] if index < len(row) else "" for row in data_rows], label)
    return {
        "header_row": header_row,
        "headers": headers,
        "data_rows": len(data_rows),
        "max_row": sheet.max_row,
        "max_column": sheet.max_column,
        "frozen_panes": str(getattr(sheet, "freeze_panes", "")) or None,
        "filters": getattr(getattr(sheet, "auto_filter", None), "ref", None),
        "tables": list(sheet.tables.keys()) if hasattr(sheet, "tables") else [],
        "columns": columns,
    }


def main():
    report = {"privacy": "Direct identifiers and message text are excluded from this profile.", "workbooks": {}}
    for path in sorted(SOURCE_DIR.glob("*.xlsx")):
        workbook = load_workbook(path, read_only=True, data_only=False)
        report["workbooks"][path.name] = {
            "size_bytes": path.stat().st_size,
            "sheet_names": workbook.sheetnames,
            "defined_names": sorted(name.name for name in workbook.defined_names.values()),
            "sheets": {sheet.title: profile_sheet(sheet) for sheet in workbook.worksheets},
        }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
