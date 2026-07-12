from tensorflow.keras.models import load_model
import joblib
import os

MODEL_PATH = "ml/warehouse_gru.keras"
SCALER_PATH = "ml/scaler.pkl"

_model = None
_scaler = None

def load_resources(force_reload=False):
    # Loads the GRU model and scaler. If already loaded, returns the cached versions from disk
    global _model
    global _scaler

    if _model is None or force_reload:
        print("Loading GRU model...")
        _model = load_model(MODEL_PATH)

    if _scaler is None or force_reload:
        print("Loading scaler...")
        _scaler = joblib.load(SCALER_PATH)
    return _model, _scaler

def get_model():
    return load_resources()[0]

def get_scaler():
    return load_resources()[1]

def reload_model():
    # Force reload after retraining.
    load_resources(force_reload=True)