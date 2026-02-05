def truncate(text, length=80):
    if not text:
        return ""
    return text if len(text) <= length else text[:length] + "..."
