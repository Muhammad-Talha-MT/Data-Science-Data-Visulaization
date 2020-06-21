# import improtant libraries
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Initial Text
st.title('Motor Vehicle Collisions In New York City')
st.markdown("## This application is streamlit dashboard that can be used "
            "to analyze motor vehicle collision in NYC 🗽")

# Load data from CSV file
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv('Motor_Vehicle_Collisions_-_Crashes.csv', nrows=nrows, parse_dates=[
                       ['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

# loading initial 100000 rows
data = load_data(100000)

# necessary data refinement
st.header("Where the most people injured in NYC")
injured_people = st.slider(
    "Number of Person injured in Vehicle Collision in NYC", 0, 19)
st.map(data.query("injured_persons >= @injured_people")
       [["latitude", "longitude"]].dropna(how='any'))

# first module
st.header("How many collision occurs during given timr of day")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle Collisions between %i:00 and %i:00" %
            (hour, (hour+1) % 24))
midpoint = [np.average(data['latitude']), np.average(data['longitude'])]
st.write(pdk.Deck(
    map_style="mapbox://style/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 8,
        "pitch": 60,
    },
    layers=[pdk.Layer("HexagonLayer",
                      data=data[['date/time', 'latitude', 'longitude']],
                      get_position=['longitude', 'latitude'],
                      radius=100,
                      extruded=True,
                      pickable=True,
                      elevation_scale=4,
                      elevation_range=[0, 1000]),

            ]

))

# second module
st.subheader("Collision by minute between %i:00 and %i:00" %
             (hour, (hour+1) % 24))
filtered = data[(data['date/time'].dt.hour == hour) &
                (data['date/time'].dt.hour < hour+1)]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(0, 60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes',
             hover_data=['minute', 'crashes'], height=400)
st.write(fig)



# third module
st.header("Top 5 dangerous streats by affected type")
select = st.selectbox("Affected Type People", [
                      'Pedestrain', 'Cyclists', 'Motoists'])
if select == 'Pedestrain':
    st.write(data.query("injured_pedestrians>=1")
             [["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])
elif select == 'Cyclists':
    st.write(data.query("injured_cyclists>=1")
             [["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])
elif select == 'Motoists':
    st.write(data.query("injured_motorists>=1")
             [["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])


# forth module
if st.checkbox("Show data of motor vehicle collisions in NYC", False):
    st.subheader("Raw Data")
    st.write(data)
