from __future__ import annotations

from abc import ABC, abstractmethod


class PaymentProvider(ABC):
    @abstractmethod
    def create_checkout_session(self, user: dict, plan: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_subscription(self, provider_subscription_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_subscription(self, provider_subscription_id: str) -> dict:
        raise NotImplementedError


class BillingDisabledProvider(PaymentProvider):
    def create_checkout_session(self, user: dict, plan: dict) -> dict:
        raise RuntimeError("Billing is disabled; no payment provider is configured")

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        raise RuntimeError("Billing is disabled; webhooks are unavailable")

    def get_subscription(self, provider_subscription_id: str) -> dict:
        raise RuntimeError("Billing is disabled; no provider subscription exists")

    def cancel_subscription(self, provider_subscription_id: str) -> dict:
        raise RuntimeError("Billing is disabled; no provider subscription exists")
