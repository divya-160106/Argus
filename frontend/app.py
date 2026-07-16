import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

st.set_page_config(page_title="Argus", layout="wide" )
def load_css(file_name):
    css_path = Path(__file__).parent / file_name
    with open(css_path) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )
load_css("style.css")
st.title("Argus")
st.subheader("AI Warehouse Congestion Prediction")

# Base Url
BASE_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)
# Cache Predictions to be quick
@st.cache_data(ttl=10)
def get_prediction():
    return requests.get(f"{BASE_URL}/predict").json()

prediction = get_prediction()

prediction_df = pd.DataFrame(prediction)
PREDICTION_COLUMNS = {
    "date": "Date",
    "day": "Day",
    "hour": "Hour",
    "truck_arrival_rate": "Truck Arrivals",
    "workers_present": "Workers",
    "queue_length": "Queue Length",
    "congestion_score": "Congestion Score",
    "waiting_time": "Waiting Time (mins)",
    "occupied_docks": "Occupied Docks",
    "waiting_trucks": "Waiting Trucks",
    "weather": "Weather",
    "timestamp": "Time Stamp"
}
prediction_df.rename(columns=PREDICTION_COLUMNS, inplace=True)

# Cache Warehouse records to be quick
@st.cache_data(ttl=10)
def get_records(page):
    return requests.get(
        f"{BASE_URL}/warehouse",
        params={"page": page}
    ).json()

# Prediction Table
st.subheader("AI Prediction Forecast")
available_dates = prediction_df["Date"].unique()
selected_date = st.selectbox("Filter by Date", available_dates)
filtered_prediction = prediction_df[prediction_df["Date"] == selected_date]
filtered_prediction = filtered_prediction.copy()

for col in ["Congestion Score", "Waiting Time (mins)"]:
    filtered_prediction[col] = filtered_prediction[col].round(2)

low = prediction_df["Congestion Score"].quantile(0.33)
high = prediction_df["Congestion Score"].quantile(0.66)
def congestion_level(score):
    if score <= low:
        return "Low"
    elif score <= high:
        return "Medium"
    else:
        return "High"   
filtered_prediction["Congestion"] = filtered_prediction["Congestion Score"].apply(congestion_level)
cols = filtered_prediction.columns.tolist()
cols.remove("Congestion")
cols.insert(0, "Congestion")
filtered_prediction = filtered_prediction[cols]

st.dataframe( filtered_prediction, use_container_width=True,
    column_config={ col: st.column_config.Column(width="medium")
        for col in filtered_prediction.columns
    }
)

score = filtered_prediction["Congestion Score"].mean()
if score <= 41:
    st.success("🟢 Warehouse Status: Low Congestion")
elif score <= 42:
    st.warning("🟡 Warehouse Status: Moderate Congestion")
else:
    st.error("🔴 Warehouse Status: High Congestion")

#Table
if "page" not in st.session_state:
    st.session_state.page = 1
response = get_records(st.session_state.page)
records = response["data"]

df = pd.DataFrame(records)
st.subheader("Warehouse Records")
COLUMN_NAMES = {
    "date": "Date",
    "day": "Day",
    "hour": "Hour",
    "truck_arrival_rate": "Truck Arrivals",
    "total_incoming_packages": "Incoming Packages",
    "processed_packages": "Processed Packages",
    "queue_length": "Queue Length",
    "workers_present": "Workers",
    "conveyor_utilization": "Conveyor Utilization (%)",
    "conveyor_speed": "Conveyor Speed",
    "avg_processing_time": "Avg Processing Time",
    "occupied_docks": "Occupied Docks",
    "waiting_trucks": "Waiting Trucks",
    "weather": "Weather",
    "congestion_score": "Congestion Score",
    "waiting_time": "Waiting Time (mins)",
    "timestamp": "Time Stamp",
}
df.rename(columns=COLUMN_NAMES, inplace=True)

st.dataframe(df, use_container_width=True,
    column_config={
        col: st.column_config.Column(width="medium") for col in df.columns
    })
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅ Previous", use_container_width=True) and st.session_state.page > 1:
        st.session_state.page -= 1
        st.rerun()
with col2:
    pages = list(range(1, response["total_pages"] + 1))
    selected_page = st.selectbox(
        "Page",
        pages,
        index=st.session_state.page - 1,
        label_visibility="collapsed"
    )
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()
with col3:
    if st.button("Next ➡", use_container_width=True) and st.session_state.page < response["total_pages"]:
        st.session_state.page += 1
        st.rerun()
st.markdown(
    f"<div style='text-align:center;'>Page <b>{st.session_state.page}</b> of <b>{response['total_pages']}</b></div>",
    unsafe_allow_html=True
)