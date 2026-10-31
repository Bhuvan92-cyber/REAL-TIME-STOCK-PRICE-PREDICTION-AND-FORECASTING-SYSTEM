from __future__ import annotations

from api.database import SupabaseDatabase
from api.subscriptions.service import EntitlementService


def enforce_limit(db: SupabaseDatabase, user_id: str, resource: str, table: str) -> None:
    EntitlementService(db).resource_limit(user_id, resource, table)


def record_usage(db: SupabaseDatabase, user_id: str, metric: str) -> None:
    EntitlementService(db).consume(user_id, metric)
