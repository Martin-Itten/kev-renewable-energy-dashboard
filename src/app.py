import streamlit as st
import pandas as pd
import json
from copy import deepcopy
import plotly.express as px

@st.cache_data
def load_csv(path:str) -> pd.DataFrame:
    data = pd.read_csv(path)
    return data

@st.cache_data
def load_json(path:str) -> object:
    with open(path) as f:
        geodata = json.load(f)
    return geodata


# Import data
powerplants_raw = load_csv('./data/raw/renewable_power_plants_CH.csv')
powerplants = deepcopy(powerplants_raw)
powerplants['commissioning_date'] = pd.to_datetime(powerplants['commissioning_date'])
powerplants['contract_period_end'] = pd.to_datetime(powerplants['contract_period_end'])

geodata_raw = load_json('./data/raw/georef-switzerland-kanton.geojson')
geodata = deepcopy(geodata_raw)

feature_id_key_raw = load_json('data/raw/feature_id_key.json')
feature_id_key = deepcopy(feature_id_key_raw)

# Layout
st.title('KEV subsidised powerplants in Switzerland')

# Electrical capacity by technology
st.subheader('Installed electrical capacity by technology')
technology_share = powerplants.groupby(by='energy_source_level_2').agg({'electrical_capacity':'sum'})
fig = px.pie(
    technology_share,
    values='electrical_capacity',
    names=technology_share.index,
    color_discrete_sequence=px.colors.sequential.algae,
)
st.plotly_chart(fig)

# To be implemented:
# Installed capacity over time
# st.subheader('Installed electrical capacity over time')


# Installed electrical capacity by canton
st.subheader('Installed electrical capacity by canton')
technologies = powerplants['energy_source_level_2'].unique().tolist()
selection = st.multiselect("Technologies", technologies, default=technologies)

cap_per_canton = powerplants.groupby(by=['canton', 'energy_source_level_2'], as_index=False) \
    .agg({'electrical_capacity':'sum'}) \
    .pivot(index='canton', columns='energy_source_level_2', values='electrical_capacity') \
    .fillna(0) 
cap_per_canton['Installed electrical capacity in MW'] = cap_per_canton[selection].sum(axis=1)
cap_per_canton['Kanton'] = cap_per_canton.apply((lambda row: feature_id_key[row.name]), axis=1)

fig = px.choropleth_mapbox(
    cap_per_canton,
    geojson=geodata,
    color='Installed electrical capacity in MW',
    locations='Kanton',
    featureidkey="properties.kan_name",
    color_continuous_scale=px.colors.sequential.algae,
    )

fig.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=6, mapbox_center = {"lon": 8.2328637, "lat": 46.7995666})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

# To be implemented:
# Installed electrical capacity by canton and technology
# st.subheader('Installed electrical capacity by canton and technology')
