from transformers import pipeline

# Zero-shot classifier
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

FOODS = ["sugar", "salt", "oil", "vegetables", "protein", "fried food", "snacks", "fruits", "dairy", "whole grains"]

def bert_mapping(text):
    rules = {"avoid": [], "reduce": [], "increase": []}

    for food in FOODS:
        result = classifier(
            text,
            candidate_labels=[
                f"avoid {food}",
                f"reduce {food}",
                f"increase {food}"
            ]
        )
        label = result["labels"][0]

        if "avoid" in label:
            rules["avoid"].append(food)
        elif "reduce" in label:
            rules["reduce"].append(food)
        elif "increase" in label:
            rules["increase"].append(food)

    return rules
