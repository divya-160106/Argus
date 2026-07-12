from simulator import WarehouseSimulator
from database import warehouse_collection

sim = WarehouseSimulator()
warehouse_collection.delete_many({})

NUM_RECORDS = 5000
for _ in range(NUM_RECORDS):
    state = sim.next_state()
    warehouse_collection.insert_one( state.model_dump() )

print("Database seeded successfully!")