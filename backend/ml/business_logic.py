TOTAL_DOCKS = 6
REQUIRED_WORKERS = 15
AVERAGE_PACKAGES_PER_TRUCK = 90
AVERAGE_PROCESSING_FACTOR = 40
QUEUE_TO_WAITING_RATIO = 40

def calculate_incoming_packages(truck_arrival_rate):
    return int( truck_arrival_rate * AVERAGE_PACKAGES_PER_TRUCK )

def calculate_processing_capacity(workers, conveyor_speed):
    return int( workers * conveyor_speed * AVERAGE_PROCESSING_FACTOR )

def calculate_docks(truck_arrival_rate):
    occupied = min( TOTAL_DOCKS, truck_arrival_rate )
    waiting = max( 0, truck_arrival_rate - occupied )
    return occupied, waiting

def calculate_queue( previous_queue, incoming_packages, processed_packages ):
    queue = ( previous_queue + incoming_packages - processed_packages )
    return max(0, queue)

def calculate_congestion( queue, utilization, truck_arrivals ):
    return min( 100, ( queue / 10 + utilization * 0.4 + truck_arrivals * 3 ) )


def calculate_business_metrics( prediction, previous_state ):
    incoming_packages = calculate_incoming_packages( prediction["truck_arrival_rate"] )
    processing_capacity = calculate_processing_capacity( prediction["workers_present"], prediction["conveyor_speed"] )
    processed_packages = min( previous_state["queue_length"] + incoming_packages, processing_capacity )
    occupied_docks, waiting_trucks = calculate_docks( prediction["truck_arrival_rate"] )
    queue = calculate_queue(
        previous_state["queue_length"],
        incoming_packages,
        processed_packages
    )
    congestion = calculate_congestion(
        queue,
        prediction["conveyor_utilization"],
        prediction["truck_arrival_rate"]
    )
    waiting_time = round( queue / QUEUE_TO_WAITING_RATIO, 2 )
    prediction.update({
        "total_incoming_packages":
            incoming_packages,
        "processed_packages":
            processed_packages,
        "queue_length":
            queue,
        "occupied_docks":
            occupied_docks,
        "waiting_trucks":
            waiting_trucks,
        "congestion_score":
            round(congestion, 2),
        "waiting_time":
            waiting_time,
        "required_workers":
            REQUIRED_WORKERS,
        "total_docks":
            TOTAL_DOCKS
    })
    return prediction