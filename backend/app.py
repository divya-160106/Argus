from fastapi import FastAPI, Query
from database import warehouse_collection
from ml.predict import predict_next_state
from fastapi.middleware.cors import CORSMiddleware

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
def get_warehouse_data( limit: int = Query(default=10, ge=1, le=1000), 
    date: str | None = None,
    day: str | None = None,
    hour: int | None = Query(default=None, ge=0, le=23),
    weather: str | None = None,
    min_workers: int | None = None,
    max_workers: int | None = None,
    min_docks: int | None = None,
    max_docks: int | None = None,
    min_trucks: int | None = None,
    max_trucks: int | None = None,
    min_congestion: float | None = None,
    max_congestion: float | None = None,
):
    query = {}

    # Exact Match Filters
    if date:
        query["date"] = date
    if day:
        query["day"] = day
    if hour is not None:
        query["hour"] = hour
    if weather:
        query["weather"] = weather

    # Worker Range
    if min_workers is not None or max_workers is not None:
        query["workers_present"] = {}
        if min_workers is not None:
            query["workers_present"]["$gte"] = min_workers
        if max_workers is not None:
            query["workers_present"]["$lte"] = max_workers

    # Occupied Docks Range
    if min_docks is not None or max_docks is not None:
        query["occupied_docks"] = {}
        if min_docks is not None:
            query["occupied_docks"]["$gte"] = min_docks
        if max_docks is not None:
            query["occupied_docks"]["$lte"] = max_docks

    # Truck Arrival Range
    if min_trucks is not None or max_trucks is not None:
        query["truck_arrival_rate"] = {}
        if min_trucks is not None:
            query["truck_arrival_rate"]["$gte"] = min_trucks
        if max_trucks is not None:
            query["truck_arrival_rate"]["$lte"] = max_trucks

    # Congestion Score Range
    if min_congestion is not None or max_congestion is not None:
        query["congestion_score"] = {}
        if min_congestion is not None:
            query["congestion_score"]["$gte"] = min_congestion
        if max_congestion is not None:
            query["congestion_score"]["$lte"] = max_congestion

    # Fetch Data
    docs = list(
        warehouse_collection.find( query, {"_id": 0} )
        .sort([ ("date", -1), ("hour", -1) ])
        .limit(limit)
    )
    return docs

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
    return predict_next_state()
