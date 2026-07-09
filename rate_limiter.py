"""
Rate Limiter
يحمي الـ API من الـ abuse — 20 طلب/ساعة لكل IP
"""
import time
from collections import defaultdict

from config.settings import RATE_LIMIT_MAX, RATE_LIMIT_WINDOW

_store: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(ip: str) -> bool:
    """
    يتحقق إذا كان الـ IP تجاوز الحد المسموح.
    يسجّل الطلب الحالي تلقائياً إذا لم يتجاوز.
    """
    now = time.time()
    _store[ip] = [t for t in _store[ip] if now - t < RATE_LIMIT_WINDOW]

    if len(_store[ip]) >= RATE_LIMIT_MAX:
        return True

    _store[ip].append(now)
    return False
