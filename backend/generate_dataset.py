import pandas as pd
from simulator import WarehouseSimulator

NUM_RECORDS = 10000

def generate_dataset():
    simulator = WarehouseSimulator()
    data = []
    for _ in range(NUM_RECORDS):
        state = simulator.next_state()
        data.append(state.model_dump())
    df = pd.DataFrame(data)
    df.to_csv("warehouse_data.csv", index=False)
    print(f"Generated {NUM_RECORDS} records successfully!")

if __name__ == "__main__":
    generate_dataset()