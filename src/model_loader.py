import joblib
import os


def load_model():
    current_dir = os.path.dirname(__file__)
    model_path = os.path.join(current_dir, "models", "random_forest_model.pkl")

    model = joblib.load(model_path)
    return model
