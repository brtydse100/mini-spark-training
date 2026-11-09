def amount(v):
    if v is None:
        return 1
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, float):
        return v
    return int(v)
