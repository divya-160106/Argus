from fastapi import FastAPI, Query
from database import warehouse_collection
from ml.predict import predict_future
from fastapi.middleware.cors import CORSMiddleware
from prediction_cache import get_predictions, set_predictions

app = FastAPI( title="Argus", version="1.0.0" )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "API_URL",
        "http://localhost:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Argus API is running!"
    }

@app.get("/warehouse")
def get_warehouse_data( page: int = Query(default=1, ge=1), page_size: int = Query(default=100, ge=1, le=100) ):
    skip = (page - 1) * page_size
    total_records = warehouse_collection.count_documents({})
    docs = list(
        warehouse_collection.find({}, {"_id": 0})
        .sort([("date", -1), ("hour", -1)])
        .skip(skip)
        .limit(page_size)
    )
    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": (total_records + page_size - 1) // page_size,
        "data": docs
    }

@app.get("/dates")
def get_available_dates():
    dates = warehouse_collection.distinct("date")
    dates.sort(reverse=True)
    return dates

@app.get("/filters")
def get_filters():
    DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]
    dates = warehouse_collection.distinct("date")
    dates.sort(reverse=True)
    days = warehouse_collection.distinct("day")
    days = [day for day in DAY_ORDER if day in days]
    weather = warehouse_collection.distinct("weather")
    weather.sort()
    return { "dates": dates, "days": days, "weather": weather }

@app.get("/predict")
def predict():
    cached = get_predictions()

    if cached is None:
        cached = predict_future()
        set_predictions(cached)

    return cached
