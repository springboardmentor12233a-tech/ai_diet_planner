import re

def gpt_interpretation_logic(text, image_text=""):
    """
    Analyzes text for clinical triggers and returns actionable diet rules.
    """
    combined_context = (str(text) + " " + image_text).lower()
    rules = []
    
    mapping = {
        'sugar|glucose|diabetes|rbs': "Diabetes Control: Low glycemic index, avoid refined sugars.",
        'pressure|bp|hypertension': "Heart Health: Low sodium (DASH diet), rich in potassium.",
        'cholesterol|lipid|statins': "Cholesterol Management: Low saturated fat, high soluble fiber.",
        'weight|obese|bmi|overweight': "Weight Management: High protein, calorie deficit.",
        # NEW: Triggers for CBC and Inflammation parameters
        'hemoglobin|hb|rbc|anemia': "Iron-Rich Diet: Increase green leafy vegetables, beans, and lean red meats.",
        'crp|inflammation|infection': "Anti-Inflammatory Diet: Increase Omega-3, turmeric, and antioxidants.",
        'fever|infection|cough|flu': "Immune Support: Maintain high hydration and Vitamin C intake."
    }
    
    found_clinical_trigger = False
    for pattern, rule in mapping.items():
        if re.search(pattern, combined_context):
            rules.append(rule)
            found_clinical_trigger = True
            
    return list(set(rules)), found_clinical_trigger