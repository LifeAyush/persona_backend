import os

_raw = [
    token.strip()
    for token in os.environ.get("RAPIDO_TOKENS", "").split(",")
    if token.strip()
]
tokens_list = _raw or [""]

__all__ = [
    "tokens_list",
]
