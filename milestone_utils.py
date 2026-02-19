import easyocr
import cv2
import pandas as pd
import re
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np

# Milestone-1: OCR Extraction
def ocr_extract_text(file):
    reader = easyocr.Reader(['en'])
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    results = reader.readtext(image)
    return " ".join([text for _, text, _ in results])

# Milestone-2: Diabetes Prediction
class DiabetesModel:
    def __init__(self, csv_path='diabetes.csv'):
        self.csv_path = csv_path
        self.scaler = StandardScaler()
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            reg_alpha=1,
            reg_lambda=1.5,
            subsample=0.7,
            colsample_bytree=0.7,
            eval_metric='logloss',
            random_state=42
        )
        self._train_model()

    def _train_model(self):
        df = pd.read_csv(self.csv_path)

        cols_to_fix = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        for col in cols_to_fix:
            median_val = df[df[col] != 0][col].median()
            df[col] = df[col].replace(0, median_val)

        df.rename(columns={'DiabetesPedigreeFunction': 'DPF'}, inplace=True)

        X = df.drop('Outcome', axis=1)
        y = df['Outcome']

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)

    def predict(self, input_dict):
        df_input = pd.DataFrame([input_dict])

        df_input = df_input[[
            "Pregnancies",
            "Glucose",
            "BloodPressure",
            "SkinThickness",
            "Insulin",
            "BMI",
            "DPF",
            "Age"
        ]]

        X_scaled = self.scaler.transform(df_input)
        return int(self.model.predict(X_scaled)[0])


def predict_diabetes(input_dict):
    model = DiabetesModel()
    return model.predict(input_dict)

# Milestone-3: Rule-Based NLP
RULES = {
    "avoid sugar": {
        "tag":"Avoid Sugar",
        "Breakfast":["Vegetable omelette","Whole-grain toast","Unsweetened tea"],
        "Lunch":["Brown rice","Dal","Fresh vegetable salad (no sweets)"],
        "Dinner":["Grilled paneer/chicken","Steamed vegetables"],
        "Snacks":["Roasted chana","Nuts"]
    },
    "reduce salt":{
        "tag":"Reduce Salt",
        "Lunch":["Low-sodium dal","Steamed vegetables"],
        "Dinner":["Grilled protein","Clear vegetable soup (no added salt)"]
    },
    "eat leafy":{
        "tag":"Increase Leafy Vegetables",
        "Lunch":["Palak dal","Brown rice","Cucumber salad"],
        "Dinner":["Spinach sauté","Paneer/chicken"]
    },
    "high fiber":{
        "tag":"High Fiber Diet",
        "Breakfast":["Oats","Apple","Flaxseed"],
        "Snacks":["Fruit bowl","Soaked almonds"]
    },
    "eat carbohydrates":{
        "tag":"Include Carbohydrates",
        "Breakfast":["Oats","Whole grain toast"],
        "Lunch":["Brown rice","Roti","Whole grain pasta"],
        "Dinner":["Quinoa","Brown rice","Vegetables"],
        "Snacks":["Whole-grain crackers","Fruits"]
    },
    "increase protein":{
        "tag":"Increase Protein Intake",
        "Breakfast":["Eggs","Paneer"],
        "Lunch":["Grilled chicken","Dal","Lentils"],
        "Dinner":["Paneer","Tofu","Fish"],
        "Snacks":["Nuts","Greek yogurt"]
    },
    "drink_water":{
        "tag":"Hydration",
        "Breakfast":["Water","Lemon water"],
        "Lunch":["Water before meal"],
        "Dinner":["Water"],
        "Snacks":["Herbal teas","Water"]
    },
    "avoid_processed_food":{
        "tag":"Avoid Processed Foods",
        "Breakfast":["Whole-grain toast","Eggs","Oatmeal"],
        "Lunch":["Homemade salad","Grilled protein"],
        "Dinner":["Steamed vegetables","Grilled fish or tofu"],
        "Snacks":["Nuts","Seeds","Fresh fruits"]
    },
    "healthy_fats":{
        "tag":"Include Healthy Fats",
        "Breakfast":["Avocado slices","Flax seeds","Chia seeds"],
        "Lunch":["Olive oil dressing on salad","Nuts"],
        "Dinner":["Olive oil","Fatty fish like salmon"],
        "Snacks":["Almonds","Walnuts"]
    },
    "low_gi_carbs":{
        "tag":"Low Glycemic Index Carbs",
        "Breakfast":["Steel-cut oats","Whole-grain bread"],
        "Lunch":["Quinoa","Barley","Brown rice (small portion)"],
        "Dinner":["Vegetable stew with lentils","Brown rice or millet"],
        "Snacks":["Whole-grain crackers","Berries"]
    },
    "limit_sweets":{
        "tag":"Limit Sweets",
        "Breakfast":["Unsweetened tea or coffee"],
        "Lunch":["Fruit instead of dessert"],
        "Dinner":["Avoid sugary desserts"],
        "Snacks":["Dark chocolate (<20g occasionally)"]
    },
    "increase_omega3":{
        "tag":"Increase Omega-3 Intake",
        "Breakfast":["Chia seeds","Flaxseed"],
        "Lunch":["Grilled salmon or sardines"],
        "Dinner":["Tofu or fish with vegetables"],
        "Snacks":["Walnuts","Pumpkin seeds"]
    }
}

KEYWORDS = {
    "avoid sugar":["avoid sugar","no sugar","skip sweets","avoid drinks","refrain from sugar","refrain from sweets","do not eat sugar","avoid sweet foods","no sweets","cut down sugar","processed sugars"],
    "reduce salt":["reduce salt","low salt","avoid salt","limit salt","cut down salt","less sodium","reduce sodium"],
    "eat leafy":["eat leafy","leafy vegetables","more greens","spinach","palak","eat vegetables","include vegetables","take greens","green vegetables","consume vegetables"],
    "high fiber":["high fiber","fiber rich","oats","bran","take fiber","eat fiber","increase fiber","increase fiber intake","fiber foods"],
    "eat carbohydrates":["eat carbohydrates","carbs","eat carbs","rice","roti","pasta","whole grains","take carbs","include carbs"],
    "increase protein":["increase protein","eat protein","protein","chicken","paneer","eggs","dal","tofu","fish","legumes","take protein","prioritize protein","protein foods"],
    "drink_water":["drink water","hydration","water intake","lemon water","herbal tea"],
    "avoid_processed_food":["avoid processed food","no junk","skip fast food","no packaged food","avoid canned food"],
    "healthy_fats":["healthy fats","avocado","olive oil","nuts","chia seeds","flax seeds"],
    "low_gi_carbs":["low glycemic carbs","low gi carbs","low gi rice","barley","quinoa","millet"],
    "limit_sweets":["limit sweets","avoid dessert","reduce sugar","no chocolate","no sweets","skip cake"],
    "increase_omega3":["omega 3","chia","flaxseed","salmon","walnuts","sardines","pumpkin seeds"]
}

def extract_rules(text):
    text_lower = text.lower()
    found_rules = []

    for rule, keywords in KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found_rules.append(rule)
                break

    return list(dict.fromkeys(found_rules))

# Weekly Diet Engine 
def generate_diet_plan(found_rules, diabetic_status=0):

    master = {"Morning": [], "Lunch": [], "Evening": [], "Night": []}

    for rule in found_rules:
        if rule == "avoid sugar" and diabetic_status == 0:
            continue

        rule_plan = RULES[rule]

        for meal, items in rule_plan.items():
            if meal == "Breakfast":
                master["Morning"].extend(items)
            elif meal == "Lunch":
                master["Lunch"].extend(items)
            elif meal == "Snacks":
                master["Evening"].extend(items)
            elif meal == "Dinner":
                master["Night"].extend(items)

    for meal in master:
        master[meal] = list(dict.fromkeys(master[meal]))

    days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    weekly_plan = {}

    for i, day in enumerate(days):
        weekly_plan[day] = {}
        for meal in master:
            foods = master[meal]
            rotated = foods[i:] + foods[:i] if foods else []
            weekly_plan[day][meal] = rotated[:4]

    return weekly_plan

def generate_weekly_plan(found_rules, diabetic_status=0):
    return generate_diet_plan(found_rules, diabetic_status)