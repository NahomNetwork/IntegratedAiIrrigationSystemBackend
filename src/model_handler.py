import pickle
import os
from sklearn.base import BaseEstimator
from typing import Optional

MODEL_PATH = "model/lgbm_model.pkl"

model: Optional[BaseEstimator] = None


def load_model() -> BaseEstimator:
    global model
    if model is None:
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
    return model
