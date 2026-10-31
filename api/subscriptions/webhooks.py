from __future__ import annotations

import hashlib
import hmac
import json


def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_event(payload: bytes) -> dict:
    event = json.loads(payload)
    if not isinstance(event, dict) or not isinstance(event.get("id"), str) or not isinstance(event.get("type"), str):
        raise ValueError("Invalid billing event")
    return event
