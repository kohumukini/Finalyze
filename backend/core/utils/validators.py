def dedupe_strings(v: list[str]) -> list[str]:
    """Drop repeated strings, ignoring case, keeping first-seen order and first-seen casing.

    Used as an AfterValidator: Pydantic has already confirmed `v` is a list of stripped,
    non-empty strings, so nothing here re-checks types or whitespace.
    """
    seen: set[str] = set()
    unique: list[str] = []
    for item in v:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
