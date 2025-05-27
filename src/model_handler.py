import pickle
import os
from sklearn.base import BaseEstimator
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "lgbm_model.pkl"


def load_model() -> BaseEstimator | None:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    try:
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
                return model
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")
