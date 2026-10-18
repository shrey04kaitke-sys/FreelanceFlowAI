import csv
import io
from typing import Iterable


def _safe_cell(value: object) -> object:
    if isinstance(value, str) and value[:1] in {"=", "+", "-", "@"}:
        return "'" + value
    return value


def markdown_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def csv_bytes(rows: Iterable[dict]) -> bytes:
    rows = list(rows)
    if not rows:
        return b""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows({key: _safe_cell(value) for key, value in row.items()} for row in rows)
    return output.getvalue().encode("utf-8")
