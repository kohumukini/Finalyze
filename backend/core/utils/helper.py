import uuid


def fence(label: str, body: str) -> str:
    """Wrap untrusted text in start/end tags that share a fresh random id.

    The id is new on every call and never shown to the user, so text inside `body` cannot forge a matching end tag.
    """
    nonce = uuid.uuid4()
    return f'<start_{label} id="{nonce}" />\n{body}\n<end_{label} id="{nonce}" />'
