KEYWORDS = [
    "avoid", "reduce", "less", "low", "cut", "limit",
    "increase", "more", "boost", "diet", "salt",
    "sugar", "oil", "fat", "vegetable", "greens",
    "fruit", "protein", "fried", "snacks", "processed"
]

def extract_diet_advice(text):
    lines = text.split("\n")
    advice = []

    for line in lines:
        line_l = line.lower()
        if any(k in line_l for k in KEYWORDS):
            advice.append(line.strip())

    return advice
