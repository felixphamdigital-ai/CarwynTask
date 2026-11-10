# -*- coding: utf-8 -*-
"""Luan phien nhieu Gemini API key: neu 1 key loi (quota/503/429/key sai...)
thi tu dong chuyen sang key ke tiep va thu lai."""


def parse_keys(raw_text: str) -> list:
    seen = []
    for line in (raw_text or "").splitlines():
        key = line.strip()
        if key and key not in seen:
            seen.append(key)
    return seen


def call_with_rotation(keys: list, start_index: int, fn):
    """fn(api_key) -> result. Tra ve (result, index_key_da_dung).
    Neu tat ca key deu loi thi raise loi cua key cuoi cung."""
    if not keys:
        raise ValueError("Chưa có Gemini API key nào.")
    n = len(keys)
    last_error = None
    for offset in range(n):
        idx = (start_index + offset) % n
        try:
            return fn(keys[idx]), idx
        except Exception as e:
            last_error = e
            continue
    raise last_error
