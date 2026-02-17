ADVICE_KEYWORDS = [
    "avoid", "reduce", "increase", "take",
    "follow", "recommended", "diet", "exercise",
    "restrict", "limit"
]

def extract_advice_lines(text):
    lines = text.split("\n")
    advice = []

    for line in lines:
        l = line.lower()
        if any(k in l for k in ADVICE_KEYWORDS):
            advice.append(line.strip())

    return advice
