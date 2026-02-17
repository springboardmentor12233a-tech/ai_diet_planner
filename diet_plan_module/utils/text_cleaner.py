import re

def clean_text(text):
    text = text.lower()

    # Remove non-letters aggressively
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Collapse spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
