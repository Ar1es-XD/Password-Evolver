def sanitize_text(value: str) -> str:
    trimmed = value.strip()
    cleaned = "".join(char for char in trimmed if char.isprintable())
    return cleaned
