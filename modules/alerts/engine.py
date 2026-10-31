from __future__ import annotations

from datetime import datetime, timedelta, timezone


def evaluate_price_alert(
    rule: dict,
    price: float | None,
    now: datetime | None = None,
) -> bool:
    if not rule.get("active", True) or price is None:
        return False
    now = now or datetime.now(timezone.utc)
    last = rule.get("last_triggered_at")
    cooldown = int(rule.get("cooldown_minutes", 60))
    if last:
        last_time = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
        if now - last_time < timedelta(minutes=cooldown):
            return False
    threshold = float(rule["threshold"])
    condition = rule.get("condition")
    if condition == "above":
        return price > threshold
    if condition == "below":
        return price < threshold
    raise ValueError(f"Unsupported alert condition: {condition}")


def event_key(rule: dict, observed_price: float, evaluated_at: datetime) -> str:
    return f"{rule['id']}:{evaluated_at.astimezone(timezone.utc).isoformat()}:{observed_price:.8f}"
