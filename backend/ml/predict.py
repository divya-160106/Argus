import numpy as np
import pandas as pd
from database import warehouse_collection
from config import MODEL_FEATURES, SEQUENCE_LENGTH
from datetime import datetime, timedelta
from ml.model_loader import ( get_model, get_scaler )
from ml.business_logic import calculate_business_metrics

#Helper for weather preprocessing
def prepare_input(df):
    df = pd.get_dummies( df, columns=["weather"], prefix="weather" )
    for col in [ "weather_sunny", "weather_cloudy", "weather_rain" ]:
        if col not in df.columns:
            df[col] = 0
    return df[MODEL_FEATURES]

# Helper for MongoDB access
def load_latest_sequence():
    docs = list(
        warehouse_collection.find({}, {"_id": 0})
        .sort([("date", -1), ("hour", -1)])
        .limit(SEQUENCE_LENGTH)
    )
    docs.reverse()
    if len(docs) < SEQUENCE_LENGTH:
        raise Exception("Not enough data.")
    return pd.DataFrame(docs)

# Date time logic
def advance_datetime(previous_state):
    current = datetime.strptime( f"{previous_state['date']} {previous_state['hour']}", "%Y-%m-%d %H" )
    next_time = current + timedelta(hours=1)
    return {
        "date": next_time.strftime("%Y-%m-%d"),
        "day": next_time.strftime("%A"),
        "hour": next_time.hour,
        "timestamp": previous_state["timestamp"] + 1
    }

def predict_future(hours=168):
    history = load_latest_sequence()
    predictions = []
    for _ in range(hours):
        operational = predict_operational_state(history)
        previous_state = history.iloc[-1].to_dict()
        full_prediction = calculate_business_metrics( operational, previous_state )
        datetime_info = advance_datetime(previous_state)
        full_prediction.update(datetime_info)
        predictions.append(full_prediction)
        history = pd.concat( [ history.iloc[1:], pd.DataFrame([full_prediction]) ], ignore_index=True )
    return predictions

def predict_operational_state(sequence):
    model = get_model()
    scaler = get_scaler()

    latest = prepare_input(sequence)
    scaled = scaler.transform(latest)

    X = np.expand_dims( scaled, axis=0 )
    prediction = model.predict( X, verbose=0 )
    prediction = scaler.inverse_transform( prediction )[0]

    #Weather one hot encoding
    weather_probs = prediction[-3:]
    weather = int(np.argmax(weather_probs))
    weather_map = {
        0: "Sunny",
        1: "Cloudy",
        2: "Rain"
    }

    result = {
    "truck_arrival_rate": max(1, int(round(prediction[0]))),
    "workers_present": min(15, max(10, int(round(prediction[1])))),
    "conveyor_speed": round(float(prediction[2]), 2),
    "conveyor_utilization": round(float(prediction[3]), 2),
    "avg_processing_time": round(float(prediction[4]), 2),
    "weather": weather_map[weather]
    }

    return result