import uuid

def generate_item_id(prefix="m"):
    """
    Genera IDs cortos con prefijo, ejemplo: m_8f3a2c
    """
    return f"{prefix}_{uuid.uuid4().hex[:6]}"
