import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from database import warehouse_collection
from config import FEATURE_COLUMNS, SEQUENCE_LENGTH
from ml.model_loader import ( get_model, get_scaler )


def predict_next_state():
    # Predict the next warehouse state using the latest SEQUENCE_LENGTH records from MongoDB
    model = get_model()
    scaler = get_scaler()
    docs = list(
        warehouse_collection.find({}, {"_id": 0})
        .sort([("date", -1), ("hour", -1)])
        .limit(SEQUENCE_LENGTH)
    )
    docs.reverse()

    if len(docs) < SEQUENCE_LENGTH:
        raise Exception("Not enough data to predict.")

    df = pd.DataFrame(docs)
    latest = df[FEATURE_COLUMNS].tail(SEQUENCE_LENGTH)
    scaled = scaler.transform(latest)

    X = np.expand_dims( scaled, axis=0 )
    prediction = model.predict( X, verbose=0 )
    prediction = scaler.inverse_transform( prediction )[0]

    INTEGER_FEATURES = {
        "truck_arrival_rate",
        "total_incoming_packages",
        "processed_packages",
        "queue_length",
        "workers_present",
        "occupied_docks",
        "waiting_trucks"
    }
    result = {}
    for feature, value in zip( FEATURE_COLUMNS, prediction ):
        if feature in INTEGER_FEATURES:
            result[feature] = int(round(value))
        else:
            result[feature] = round(float(value), 2)
    return result