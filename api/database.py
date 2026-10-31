from __future__ import annotations

from typing import Any

import httpx

from api.config import settings


class SupabaseDatabase:
    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        self.base_url = f"{settings.supabase_url.rstrip('/')}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_service_key,
            "Authorization": "Bearer " + settings.supabase_service_key,
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, str] | None = None,
        payload: Any = None,
        prefer: str = "return=representation",
    ) -> list[dict[str, Any]]:
        headers = {**self.headers, "Prefer": prefer}
        try:
            response = httpx.request(
                method,
                f"{self.base_url}/{table}",
                headers=headers,
                params=params,
                json=payload,
                timeout=15,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Supabase network request failed: {exc}") from exc
        if response.status_code >= 400:
            raise RuntimeError(f"Supabase request failed ({response.status_code}): {response.text[:300]}")
        if not response.content:
            return []
        result = response.json()
        return result if isinstance(result, list) else [result]

    def rpc(self, function: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        headers = {**self.headers, "Content-Type": "application/json"}
        try:
            response = httpx.post(
                f"{self.base_url.rsplit('/rest/v1', 1)[0]}/rest/v1/rpc/{function}",
                headers=headers,
                json=payload,
                timeout=15,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Supabase RPC request failed: {exc}") from exc
        if response.status_code >= 400:
            raise RuntimeError(f"Supabase RPC failed ({response.status_code}): {response.text[:300]}")
        if not response.content:
            return []
        result = response.json()
        return result if isinstance(result, list) else [result]


def database() -> SupabaseDatabase:
    return SupabaseDatabase()
