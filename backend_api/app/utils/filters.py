def normalize_sort(value: str, allowed: dict[str, str], default: str) -> str:
    """Return a safe sort key given allowed mapping."""
    return allowed.get(value, default)
