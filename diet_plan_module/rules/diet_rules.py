DIET_RULES = {

    # ---------------- DIABETES / LOW SUGAR ----------------
    "low_sugar": {
        "avoid": [
            "sweets", "desserts", "soft drinks",
            "white bread", "cakes", "biscuits"
        ],
        "include": [
            "whole grains", "millets", "vegetables",
            "nuts", "seeds", "low glycemic fruits"
        ],
        "note": "Avoid refined carbohydrates and sugary foods"
    },

    # ---------------- HEART / FAT ----------------
    "low_fat": {
        "avoid": [
            "fried food", "junk food",
            "butter", "cream", "fast food"
        ],
        "include": [
            "steamed food", "grilled vegetables",
            "fruits", "salads", "olive oil (small quantity)"
        ],
        "note": "Prefer cooking with minimal oil"
    },

    # ---------------- BLOOD PRESSURE ----------------
    "low_sodium": {
        "avoid": [
            "salt", "pickles", "processed food",
            "chips", "packaged snacks"
        ],
        "include": [
            "fresh fruits", "vegetables",
            "home cooked meals", "curd", "coconut water"
        ],
        "note": "Avoid packaged and salty foods"
    },

    # ---------------- ANEMIA / IRON ----------------
    "iron_diet": {
        "avoid": [
            "tea", "coffee"
        ],
        "include": [
            "spinach", "beetroot", "dates",
            "lentils", "jaggery",
            "pomegranate", "raisins", "chickpeas"
        ],
        "note": "Consume vitamin C with iron-rich foods"
    },

    # ---------------- WEAKNESS / PROTEIN ----------------
    "high_protein": {
        "avoid": [],
        "include": [
            "eggs", "paneer", "dal",
            "fish", "chicken",
            "soybean", "tofu", "curd"
        ],
        "note": "Distribute protein intake evenly throughout the day"
    },

    # ---------------- DIGESTION / CONSTIPATION ----------------
    "high_fiber": {
        "avoid": [
            "refined flour", "bakery items"
        ],
        "include": [
            "oats", "whole grains",
            "vegetables", "fruits",
            "flaxseeds", "chia seeds"
        ],
        "note": "Increase fiber gradually and drink enough water"
    },

    # ---------------- WEIGHT LOSS ----------------
    "calorie_deficit": {
        "avoid": [
            "sugary food", "fried food",
            "junk food", "late night snacks"
        ],
        "include": [
            "salads", "fruits",
            "lean protein", "vegetable soup",
            "sprouts", "boiled vegetables"
        ],
        "note": "Portion control and regular physical activity are essential"
    },

    # ---------------- ACIDITY / GASTRIC ----------------
    "low_spice": {
        "avoid": [
            "spicy food", "chilli",
            "pepper", "fried food"
        ],
        "include": [
            "boiled food", "curd",
            "banana", "rice",
            "oats", "vegetable soup"
        ],
        "note": "Eat small frequent meals and avoid spicy food"
    },

    # ---------------- KIDNEY ----------------
    "low_protein_kidney": {
        "avoid": [
            "red meat", "excess protein",
            "processed food"
        ],
        "include": [
            "vegetables", "rice",
            "apple", "cabbage",
            "cauliflower"
        ],
        "note": "Protein intake should be carefully monitored"
    },

    # ---------------- LIVER ----------------
    "liver_friendly": {
        "avoid": [
            "alcohol", "fried food",
            "junk food"
        ],
        "include": [
            "fruits", "vegetables",
            "whole grains",
            "green tea", "salads"
        ],
        "note": "Avoid alcohol completely and eat light meals"
    },

    # ---------------- GENERAL FALLBACK ----------------
    "general_healthy": {
        "avoid": [
            "excess sugar", "fried food"
        ],
        "include": [
            "fruits", "vegetables",
            "whole grains", "curd"
        ],
        "note": "Maintain a balanced and healthy diet"
    }
}
