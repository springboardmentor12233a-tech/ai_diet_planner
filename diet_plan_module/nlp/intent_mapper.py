from rules.instruction_rules import INSTRUCTION_RULES
from rules.medicine_rules import MEDICINE_PATTERNS

def map_text_to_intents(text):
    intents = set()
    words = text.split()

    for phrase, intent in INSTRUCTION_RULES.items():
        if phrase in text:
            intents.add(intent)

    for word in words:
        for pattern, intent in MEDICINE_PATTERNS.items():
            if pattern in word:
                intents.add(intent)

    if not intents:
        intents.add("iron_diet") if "vit" in text else intents.add("general_healthy")

    return list(intents)
