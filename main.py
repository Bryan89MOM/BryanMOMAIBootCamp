import streamlit as st
import pandas as pd
import requests

# Load the data from the API
@st.cache_data
def load_data():
    datasetId = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
    url = f"https://data.gov.sg/api/action/datastore_search?resource_id={datasetId}&limit=5000"  # Adjust the limit as needed
    response = requests.get(url)
    data = response.json()
    records = data['result']['records']
    df = pd.DataFrame.from_records(records)
    
    # Convert columns to appropriate data types
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['lease_commence_date'] = pd.to_numeric(df['lease_commence_date'], errors='coerce')
    df['month'] = pd.to_datetime(df['month'], errors='coerce')
    
    return df

data = load_data()

# Title of the app
st.title('HDB Resale Prices in Singapore')

# Main filter options
st.header('Filter Options')
towns = st.multiselect('Select Town', data['town'].unique())
flat_types = st.multiselect('Select Flat Type', data['flat_type'].unique())
storey_ranges = st.multiselect('Select Storey Range', data['storey_range'].unique())
budget = st.number_input('Budget (SGD)', min_value=0, value=0)
lease_start_year = st.slider('Lease Commence Year', int(data['lease_commence_date'].min()), int(data['lease_commence_date'].max()), (int(data['lease_commence_date'].min()), int(data['lease_commence_date'].max())))

# Filter data based on selections
if towns:
    data = data[data['town'].isin(towns)]
if flat_types:
    data = data[data['flat_type'].isin(flat_types)]
if storey_ranges:
    data = data[data['storey_range'].isin(storey_ranges)]
data = data[(data['resale_price'] <= budget)]
data = data[(data['lease_commence_date'] >= lease_start_year[0]) & (data['lease_commence_date'] <= lease_start_year[1])]

# Display the data
st.write('### Filtered Data', data)

# Additional visualizations
st.write('### Average Resale Price by Town')
avg_price_town = data.groupby('town')['resale_price'].mean().sort_values(ascending=False)
st.bar_chart(avg_price_town)

st.write('### Resale Price Trends Over Time')
price_trends = data.groupby('month')['resale_price'].mean()
st.line_chart(price_trends)

st.write('### Distribution of Flat Types')
flat_type_distribution = data['flat_type'].value_counts()
st.bar_chart(flat_type_distribution)

st.write('### Resale Price by Storey Range')
price_by_storey = data.groupby('storey_range')['resale_price'].mean().sort_values(ascending=False)
st.bar_chart(price_by_storey)

st.write('### Resale Price by Lease Commence Date')
price_by_lease = data.groupby('lease_commence_date')['resale_price'].mean()
st.line_chart(price_by_lease)

# Display a map if latitude and longitude are available
if 'latitude' in data.columns and 'longitude' in data.columns:
    st.write('### Map of Resale Flats')
    st.map(data[['latitude', 'longitude']])
