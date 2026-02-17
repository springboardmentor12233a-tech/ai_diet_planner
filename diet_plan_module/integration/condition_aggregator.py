def aggregate_conditions(nlp_intents, ml_result=None):
    """
    Combines NLP-based diet intents with ML-based diabetes prediction.
    """

    final_conditions = set(nlp_intents)

    # ML-based diabetes → diet override
    if ml_result:
        if ml_result.get("is_diabetic") or ml_result.get("risk_probability", 0) >= 0.5:
            final_conditions.add("low_sugar")

    return list(final_conditions)
