import json
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token ' + os.getenv("TINGO_API_KEY")
}

aapl_json = requests.get(
    "https://api.tiingo.com/tiingo/daily/aapl/prices?startDate=2021-06-01&endDate=2021-12-01/", headers=headers
).json()

# Convert json to a DataFrame
aapl_df = pd.DataFrame.from_dict(aapl_json)

# Change the date to a DateTime object
aapl_df['date'] = pd.to_datetime(aapl_df['date'])

# Set the date as an index and remove the timestamp
aapl_df = aapl_df.set_index('date').tz_localize(None)

print(aapl_df.head())
print(aapl_df.columns)

# define the data
candlestick = go.Candlestick(
    x=aapl_df.index,
    open=aapl_df['adjOpen'],
    high=aapl_df['adjHigh'],
    low=aapl_df['adjLow'],
    close=aapl_df['adjClose'],
    name="OHLC"
)

# create the figure
fig = go.Figure(data=[candlestick])
  
# plot the figure
fig.show()
