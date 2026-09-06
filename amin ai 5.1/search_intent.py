def needs_search(message):
    message = message.lower()

    keywords = [
        "today",
        "now",
        "news",
        "latest",
        "price",
        "new",
        "2026"
    ]

    for word in keywords:
        if word in message:
            return True

    return False