import asyncio
from typing import Any, Dict, Callable

_registry: Dict[str, Callable] = {}

def register(name: str, fn: Callable):
    _registry[name] = fn

async def ask(name: str, payload: Any):
    if name not in _registry:
        raise ValueError(f"Agent '{name}' not found")
    # Ensure callable can be awaited
    result = _registry[name](payload)
    if asyncio.iscoroutine(result):
        return await result
    return result
