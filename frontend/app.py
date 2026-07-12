import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Argus", layout="wide" )
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("style.css")
st.title("Argus")
st.subheader("AI Warehouse Congestion Prediction")

#Base Url
BASE_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)
prediction = requests.get( f"{BASE_URL}/predict" ).json()

@st.cache_data
def get_filters():
    return requests.get(f"{BASE_URL}/filters").json()

@st.cache_data(ttl=10)
def get_records(params):
    return requests.get(
        f"{BASE_URL}/warehouse",
        params=params
    ).json()

#Columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Truck Arrivals", prediction["truck_arrival_rate"])
with col2:
    st.metric("Workers", prediction["workers_present"])
with col3:
    st.metric( "Queue", prediction["queue_length"])

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Congestion", prediction["congestion_score"])
with col5:
    st.metric("Waiting Time", prediction["waiting_time"])
with col6:
    st.metric("Conveyor Speed", prediction["conveyor_speed"])

score = prediction["congestion_score"]
if score < 40:
    st.success("🟢 Warehouse Status: Low Congestion")
elif score < 70:
    st.warning("🟡 Warehouse Status: Moderate Congestion")
else:
    st.error("🔴 Warehouse Status: High Congestion")

#Sidebar
filters = requests.get( f"{BASE_URL}/filters" ).json()
with st.sidebar:
    st.header("Filters")
    date = st.selectbox("Date", ["All"] + filters["dates"])
    day = st.selectbox("Day", ["All"] + filters["days"])
    weather = st.selectbox("Weather", ["All"] + filters["weather"])
    hour = st.number_input("Hour", 0, 23, value=0)
    record_limit = st.sidebar.slider(
        "Records to Display",
        min_value=5,
        max_value=100,
        value=10,
        step=5
    )

    params = {}
    if date != "All":
        params["date"] = date
    if day != "All":
        params["day"] = day
    if weather != "All":
        params["weather"] = weather
    params["limit"] = record_limit
    records = requests.get( f"{BASE_URL}/warehouse", params=params).json()

#Table
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