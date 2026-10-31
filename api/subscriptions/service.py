from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from api.database import SupabaseDatabase
from .plans import DEFAULT_PLANS
from .states import effective_plan


class SubscriptionError(ValueError):
    pass


class EntitlementService:
    def __init__(self, db: SupabaseDatabase):
        self.db = db

    def plan(self, user_id: str) -> dict[str, Any]:
        entitlements = self.db.request("GET", "subscriptions", params={"user_id": f"eq.{user_id}", "select": "plan_id,status,ends_at", "limit": "1"})
        if not entitlements:
            entitlements = self.db.request("GET", "user_entitlements", params={"user_id": f"eq.{user_id}", "select": "plan_id", "limit": "1"})
        entitlement = entitlements[0] if entitlements else {"plan_id": "free", "status": "FREE"}
        plan_id = effective_plan(entitlement)
        plans = self.db.request("GET", "plans", params={"id": f"eq.{plan_id}", "limit": "1"})
        if plans:
            plan = plans[0]
            return {"id": plan_id, "name": plan.get("name", plan_id.title()), "limits": plan.get("limits", {}), "features": plan.get("features", [])}
        fallback = DEFAULT_PLANS.get(plan_id, DEFAULT_PLANS["free"])
        return {"id": plan_id if plan_id in DEFAULT_PLANS else "free", **fallback}

    def usage(self, user_id: str) -> list[dict]:
        return self.db.request("GET", "usage_records", params={"user_id": f"eq.{user_id}", "order": "period_start.desc"})

    def check_feature(self, user_id: str, feature: str) -> None:
        if feature not in self.plan(user_id).get("features", []):
            raise SubscriptionError(f"Feature '{feature}' requires a higher plan")

    def consume(self, user_id: str, metric: str) -> None:
        plan = self.plan(user_id)
        limit = plan.get("limits", {}).get(metric)
        if not limit or limit.get("value") is None:
            raise SubscriptionError(f"Usage limit is not configured for {metric}")
        if limit["period"] == "total":
            raise SubscriptionError(f"Use resource_limit for total metric '{metric}'")
        period_start = self._period_start(limit["period"])
        result = self.db.rpc("consume_usage", {
            "p_user_id": user_id,
            "p_metric": metric,
            "p_period_start": period_start.isoformat(),
            "p_limit": int(limit["value"]),
        })
        if not result or not result[0].get("allowed", False):
            raise SubscriptionError(f"{plan['name']} plan limit reached for {metric} ({limit['value']} per {limit['period']})")

    def resource_limit(self, user_id: str, metric: str, table: str) -> None:
        plan = self.plan(user_id)
        limit = plan.get("limits", {}).get(metric)
        if not limit or limit.get("period") != "total":
            raise SubscriptionError(f"Usage limit is not configured for {metric}")
        rows = self.db.request("GET", table, params={"user_id": f"eq.{user_id}", "select": "id"})
        if len(rows) >= int(limit["value"]):
            raise SubscriptionError(f"{plan['name']} plan limit reached for {metric} ({limit['value']})")

    def _period_start(self, period: str) -> date:
        now = date.today()
        if period == "month":
            return now.replace(day=1)
        return now

    def account(self, user_id: str) -> dict:
        entitlement = self.db.request("GET", "user_entitlements", params={"user_id": f"eq.{user_id}", "limit": "1"})
        return {"plan": self.plan(user_id), "subscription": entitlement[0] if entitlement else {"plan_id": "free", "status": "free"}, "usage": self.usage(user_id)}
