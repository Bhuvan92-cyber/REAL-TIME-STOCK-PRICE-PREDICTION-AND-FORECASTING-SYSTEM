import json

import pytest

from api.subscriptions.service import EntitlementService, SubscriptionError
from api.subscriptions.webhooks import parse_event, verify_hmac_signature
from api.subscriptions.states import effective_plan


class FakeDatabase:
    def __init__(self):
        self.usage = 0

    def request(self, method, table, *, params=None, payload=None, prefer="return=representation"):
        if table == "subscriptions":
            return [{"plan_id": "free", "status": "FREE"}]
        if table == "plans":
            return [{"id": "free", "name": "Free", "limits": {"forecast_requests": {"period": "day", "value": 2}}, "features": ["basic_forecasting"]}]
        if table == "usage_records":
            return [{"metric": "forecast_requests", "usage_count": self.usage, "period_start": "2026-10-31"}]
        if table in {"portfolios", "watchlists"}:
            return []
        return []

    def rpc(self, function, payload):
        self.usage += 1
        return [{"allowed": self.usage <= payload["p_limit"], "usage_count": self.usage}]


def test_free_plan_feature_and_atomic_quota_contract():
    service = EntitlementService(FakeDatabase())
    assert service.plan("user")["id"] == "free"
    service.check_feature("user", "basic_forecasting")
    with pytest.raises(SubscriptionError):
        service.check_feature("user", "ensemble_forecasting")
    service.consume("user", "forecast_requests")
    service.consume("user", "forecast_requests")
    with pytest.raises(SubscriptionError):
        service.consume("user", "forecast_requests")


def test_expired_subscription_resolves_to_free():
    assert effective_plan({"plan_id": "premium", "status": "EXPIRED"}) == "free"
    assert effective_plan({"plan_id": "premium", "status": "ACTIVE"}) == "premium"


def test_webhook_signature_and_payload_validation():
    payload = json.dumps({"id": "evt_1", "type": "subscription.renewed"}).encode()
    import hashlib
    import hmac
    signature = hmac.new(b"secret", payload, hashlib.sha256).hexdigest()
    assert verify_hmac_signature(payload, signature, "secret")
    assert not verify_hmac_signature(payload, "bad", "secret")
    assert parse_event(payload)["id"] == "evt_1"
    with pytest.raises(ValueError):
        parse_event(b"{}")
