import random
from models import WarehouseState
import random
from datetime import datetime, timedelta
from models import WarehouseState

class WarehouseSimulator:
    def __init__(self):
        self.time = 0
        self.queue = 100
        self.current_datetime = datetime(2026, 7, 1, 0, 0)

    def next_state(self):
        self.time += 1
        self.current_datetime += timedelta(hours=1)
        hour = self.current_datetime.hour

        #TRUCK ARRIVALS SIMULATION-----------------
        # Rush Hour Truck Arrivals 
        if 8 <= hour <= 10:               # Morning rush
            truck_arrival_rate = random.randint(7, 10)
        elif 17 <= hour <= 20:            # Evening rush
            truck_arrival_rate = random.randint(6, 9)
        elif 0 <= hour <= 5:              # Late night
            truck_arrival_rate = random.randint(1, 3)
        else:
            truck_arrival_rate = random.randint(3, 6)

        # Weather 
        weather = random.choice([
            "Sunny",
            "Cloudy",
            "Rain"
        ])

        # Affecting truck arrivals
        if weather == "Rain":
            truck_arrival_rate = max(1, truck_arrival_rate - 1)

        total_incoming_packages = (truck_arrival_rate * random.randint(60, 120))

        #CONVEYOR BELT SIMULATION---------------------------
        # Workers
        required_workers = 15
        workers_present = random.randint(10, 15)

        # Conveyor Speed
        conveyor_speed = round(random.uniform(0.8, 1.5), 2)

        # Rain slows conveyor slightly
        if weather == "Rain":
            conveyor_speed = round(max(0.6, conveyor_speed - 0.2), 2)

        conveyor_utilization = random.randint(50, 95)
        avg_processing_time = round(random.uniform(2.5, 5.5), 2)

        # Rain increases processing time
        if weather == "Rain":
            avg_processing_time = round(avg_processing_time + 0.5, 2)

        # DOCK SIMULATION--------------------
        total_docks = 6
        occupied_docks = min(total_docks, truck_arrival_rate)
        waiting_trucks = max(0, truck_arrival_rate - occupied_docks)

        # Processing Capacity
        processing_capacity = int( workers_present * conveyor_speed * random.randint(35, 45))

        processed_packages = min(self.queue + total_incoming_packages, processing_capacity)

        self.queue += total_incoming_packages - processed_packages
        self.queue = max(self.queue, 0)

        congestion_score = (self.queue / 10 + conveyor_utilization * 0.4 + truck_arrival_rate * 3)

        waiting_time = self.queue / 40

        # Add small real-world variability
        congestion_score += random.uniform(-3, 3)
        waiting_time += random.uniform(-1, 1)

        # Keep values within valid limits
        congestion_score = max(0, min(100, congestion_score))
        waiting_time = max(0, waiting_time)

        # Round for readability
        congestion_score = round(congestion_score, 2)
        waiting_time = round(waiting_time, 2)

        day = self.current_datetime.strftime("%A")
        date = self.current_datetime.strftime("%Y-%m-%d")

        state = WarehouseState(
            timestamp=self.time,
            truck_arrival_rate=truck_arrival_rate,
            total_incoming_packages=total_incoming_packages,
            processed_packages=processed_packages,
            queue_length=self.queue,
            required_workers=required_workers,
            workers_present=workers_present,
            conveyor_utilization=conveyor_utilization,
            conveyor_speed=conveyor_speed,
            avg_processing_time=avg_processing_time,
            total_docks=total_docks,
            occupied_docks=occupied_docks,
            waiting_trucks=waiting_trucks,
            weather=weather,
            hour=hour,
            date=date,
            day=day,
            congestion_score=congestion_score,
            waiting_time=waiting_time
        )
        return state