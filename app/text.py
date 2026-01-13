from typing import Any

def content_to_text(content: Any) -> str:
    """
    Some LLM wrappers return content as:
    - str
    - list[dict|str] (parts)
    - other objects
    Convert to a stable string.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # best-effort join
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                # common keys: "text"
                if "text" in p and isinstance(p["text"], str):
                    parts.append(p["text"])
                else:
                    parts.append(str(p))
            else:
                parts.append(str(p))
        return "\n".join(parts)
    return str(content)
