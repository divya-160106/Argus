from pydantic import BaseModel

class WarehouseState(BaseModel):
    timestamp: int
    truck_arrival_rate: int
    total_incoming_packages: int
    processed_packages: int
    queue_length: int
    conveyor_utilization: float
    conveyor_speed: float
    avg_processing_time: float
    hour: int
    day: str
    date: str
    congestion_score: float
    waiting_time: float
    required_workers: int
    workers_present: int
    total_docks: int
    occupied_docks: int
    waiting_trucks: int
    weather: str