from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import main
import train_model
import numpy as np
import cv2
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

READER = main.reader


# ---------------- IMAGE PREPROCESSING ----------------

def preprocess_image(image):

    height, width = image.shape[:2]

    if max(height, width) < 1200:
        scale = 1200 / max(height, width)
        image = cv2.resize(image, None, fx=scale, fy=scale)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.medianBlur(gray, 3)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return thresh


# ---------------- MULTI PARAMETER EXTRACTION ----------------

def extract_parameters(text):

    patterns = {
        "Hemoglobin": r'(?:hemoglobin|haemoglobin|hb)[^\d]{0,10}(\d+\.?\d*)',
        "RBC": r'(?:rbc)[^\d]{0,10}(\d+\.?\d*)',
        "WBC": r'(?:wbc)[^\d]{0,10}(\d+\.?\d*)',
        "Platelets": r'(?:platelet)[^\d]{0,10}(\d+\.?\d*)',
        "Glucose": r'(?:glucose|fbs|fasting blood sugar|rbs)[^\d]{0,10}(\d+\.?\d*)',
        "HbA1c": r'(?:hba1c)[^\d]{0,10}(\d+\.?\d*)',
        "Cholesterol": r'(?:cholesterol)[^\d]{0,10}(\d+\.?\d*)',
        "Triglycerides": r'(?:triglyceride)[^\d]{0,10}(\d+\.?\d*)',
        "HDL": r'(?:hdl)[^\d]{0,10}(\d+\.?\d*)',
        "LDL": r'(?:ldl)[^\d]{0,10}(\d+\.?\d*)',
        "TSH": r'(?:tsh)[^\d]{0,10}(\d+\.?\d*)',
        "T3": r'(?:t3)[^\d]{0,10}(\d+\.?\d*)',
        "T4": r'(?:t4)[^\d]{0,10}(\d+\.?\d*)',
        "Protein": r'(?:total protein)[^\d]{0,10}(\d+\.?\d*)',
        "Albumin": r'(?:albumin)[^\d]{0,10}(\d+\.?\d*)',
        "Iron": r'(?:iron)[^\d]{0,10}(\d+\.?\d*)',
        "CRP": r'(?:crp)[^\d]{0,10}(\d+\.?\d*)',
    }

    results = {}

    for param, pattern in patterns.items():
        match = re.search(pattern, text, re.I)
        if match:
            value = match.group(1).replace(",", ".")
            try:
                results[param] = float(value)
            except:
                pass

    return results


# ---------------- DIET PLAN ----------------

def generate_7_day_plan(condition):

    pools = {
        "ANEMIC": {
            "B": ["Spinach & Egg", "Iron Cereal", "Beet Smoothie", "Oats Seeds", "Tofu Scramble", "Berry Yogurt", "Omelet"],
            "L": ["Lentils", "Chickpea Salad", "Quinoa Beans", "Turkey Wrap", "Spinach Curry", "Lamb Soup", "Soy Bowl"],
            "D": ["Grilled Steak", "Baked Fish", "Chicken", "Shrimp", "Tofu Veg", "Egg Curry", "Fortified Rice"]
        },

        "DIABETIC": {
            "B": ["Oats", "Chia Pudding", "Egg White", "Greek Yogurt", "Quinoa", "Avocado Toast", "Buckwheat"],
            "L": ["Quinoa Salad", "Lentil Soup", "Tofu Stir Fry", "Chickpea Wrap", "Grilled Fish", "Turkey Salad", "Veg Curry"],
            "D": ["Grilled Chicken", "Fish", "Stuffed Veg", "Zucchini", "Lean Beef", "Roasted Tofu", "Shrimp"]
        },

        "HYPERLIPIDEMIA": {
            "B": ["Oatmeal", "Fruit Bowl", "Low Fat Milk", "Smoothie", "Whole Toast", "Nuts", "Seeds"],
            "L": ["Brown Rice", "Veg Soup", "Salad", "Bean Curry", "Grilled Paneer", "Quinoa", "Veg Wrap"],
            "D": ["Grilled Fish", "Steamed Veg", "Chicken", "Tofu", "Lentils", "Veg Stir Fry", "Soup"]
        },

        "NORMAL": {
            "B": ["Fruit Bowl", "Toast", "Smoothie", "Muesli", "Eggs", "Pancakes", "Cereal"],
            "L": ["Sandwich", "Pasta", "Burger", "Wrap", "Rice Beans", "Salad", "Soup"],
            "D": ["Steak", "Potato", "Veg Stir Fry", "Pizza", "Shrimp", "Pasta", "Fish"]
        }
    }

    selected = pools.get(condition, pools["NORMAL"])

    return [
        {
            "day": i + 1,
            "Breakfast": selected["B"][i],
            "Lunch": selected["L"][i],
            "Dinner": selected["D"][i]
        }
        for i in range(7)
    ]


# ---------------- API ----------------

@app.post("/process-report")
async def process_report(name: str, file: UploadFile = File(...)):

    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    processed_img = preprocess_image(image)

    results = READER.readtext(
        processed_img,
        detail=0,
        paragraph=True,
        contrast_ths=0.05,
        adjust_contrast=0.7
    )

    text = " ".join(results)

    print("OCR TEXT:", text)


    # -------- PARAMETER EXTRACTION --------

    parameters = extract_parameters(text)

    insights = []

    for k, v in parameters.items():
        insights.append(f"{k}: {v}")


    # -------- DEFAULT FALLBACK --------

    if not insights:
        insights.append("Report processed successfully")
        insights.append("Clinical values may be unclear due to image quality")


    # -------- CONDITION DETECTION --------

    condition = "NORMAL"

    if "Hemoglobin" in parameters and parameters["Hemoglobin"] < 12:
        condition = "ANEMIC"

    elif "Glucose" in parameters and parameters["Glucose"] > 140:
        condition = "DIABETIC"

    elif "Cholesterol" in parameters and parameters["Cholesterol"] > 200:
        condition = "HYPERLIPIDEMIA"


    # -------- OPTIONAL ALERT ENGINE --------

    try:
        alerts = train_model.check_for_alerts(
            glucose=parameters.get("Glucose"),
            hb=parameters.get("Hemoglobin"),
            crp=parameters.get("CRP")
        )

        if alerts:
            insights.extend(alerts)

    except:
        pass


    return {
        "name": name,
        "insights": insights[:6],   # limit display
        "diet_7_days": generate_7_day_plan(condition)
    }
