# -*- coding: utf-8 -*-
"""Trich toan bo text (paragraph + table) tu 1 file .docx thanh 1 chuoi brief."""

import docx


def extract_docx_text(file_obj) -> str:
    document = docx.Document(file_obj)
    parts = []
    for p in document.paragraphs:
        if p.text.strip():
            parts.append(p.text)
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts)
