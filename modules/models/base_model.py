from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseModel(ABC):
    """Small contract shared by trainable forecasting adapters."""

    name: str
    version: str = "1.0"
    supports_features: bool = True

    @abstractmethod
    def train(self, X: Any, y: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, X: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str | Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str | Path) -> None:
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "supports_features": self.supports_features,
            "available": True,
        }
