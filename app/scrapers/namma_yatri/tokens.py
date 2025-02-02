import os
tokens_list = [
    os.environ.get("NAMMA_YATRI_TOKEN", "")
]

__all__ = [
    "tokens_list"
]