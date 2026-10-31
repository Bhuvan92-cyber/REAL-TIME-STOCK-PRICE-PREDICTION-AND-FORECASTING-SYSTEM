from __future__ import annotations

VALID_STATES = {"FREE", "TRIALING", "ACTIVE", "PAST_DUE", "CANCELLED", "EXPIRED", "SUSPENDED"}


def effective_plan(subscription: dict) -> str:
    status = str(subscription.get("status", "FREE")).upper()
    return subscription.get("plan_id", "free") if status in {"FREE", "TRIALING", "ACTIVE"} else "free"


def validate_state(status: str) -> str:
    normalized = status.upper()
    if normalized not in VALID_STATES:
        raise ValueError(f"Unsupported subscription status: {status}")
    return normalized
