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


def is_model_level_error(exc: Exception) -> bool:
    """Kiểm tra xem lỗi có phải do Model/Server Google quá tải hoặc không khả dụng
    (503 High Demand, 504 Deadline/Timeout, 404 Deprecated/Not Found) hay không."""
    msg = str(exc).lower()
    return any(err in msg for err in [
        "503", "unavailable", "high demand", "spikes in demand",
        "504", "deadline", "timeout",
        "404", "not_found", "no longer available",
    ])


def call_with_rotation(keys: list, start_index: int, fn):
    """fn(api_key) -> result. Tra ve (result, index_key_da_dung).
    Neu tat ca key deu loi thi raise loi cua key cuoi cung.
    Neu loi do Model quá tải (503), dung thu key som de chuyen sang model du phong."""
    if not keys:
        raise ValueError("Chưa có Gemini API key nào.")
    n = len(keys)
    last_error = None
    model_error_count = 0
    for offset in range(n):
        idx = (start_index + offset) % n
        try:
            return fn(keys[idx]), idx
        except Exception as e:
            last_error = e
            if is_model_level_error(e):
                model_error_count += 1
                if model_error_count >= 2:
                    # Đã thử 2 key đều báo lỗi từ model/server, dừng ngay để fallback model
                    break
            continue
    raise last_error
