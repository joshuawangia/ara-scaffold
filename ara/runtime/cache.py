"""Content-addressed, validated-output cache; no provider history is retained."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def cache_key(kind: str, template: str, inputs: str, model: str, schema: dict) -> str:
    return digest(canonical([kind, digest(template), digest(inputs), model, digest(canonical(schema))]))


class Cache:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> dict | None:
        path = self.path / f'{key}.json'
        return json.loads(path.read_text()) if path.exists() else None

    def discard(self, key: str) -> None:
        (self.path / f'{key}.json').unlink(missing_ok=True)

    def put(self, key: str, value: dict) -> None:
        path = self.path / f'{key}.json'
        try:
            with path.open('x') as stream:
                stream.write(canonical(value))
        except FileExistsError:
            if self.get(key) != value:
                raise ValueError('cache key collision or concurrent divergent output')
