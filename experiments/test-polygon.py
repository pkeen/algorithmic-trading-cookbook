from dotenv import load_dotenv
import os
import requests
import pandas as pd

# by default looks for a .env in cwd
load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

headers = {'Authorization': 'Bearer ' + POLYGON_API_KEY}

ticker = 'AAPL'
url = (
    f"https://api.polygon.io/v2/aggs/ticker/{ticker}/"
    "range/1/minute/2022-01-09/2023-01-09?"
    "adjusted=true&sort=asc&limit=50000"
)
response = requests.get(url, headers=headers).json()

print(response)

# df = pd.DataFrame(response['results'])

# df = df.rename(columns={
#     't': 'Date',
#     'o': 'Open',
#     'h': 'High',
#     'l': 'Low',
#     'c': 'Adj Close',
#     'v': 'Volume',  
#     'vw': 'Close'
#     })

# df['Date'] = pd.to_datetime(df['Date'], unit='ms')
# df.to_csv(f"polygon_{ticker}.csv", columns=['Date', 'Open', 'High', 'Low', 'Adj Close', 'Volume', 'Close'], index=False)




