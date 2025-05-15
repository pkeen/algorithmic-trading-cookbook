import pandas as pd
import requests
import os
from dotenv import load_dotenv
from io import StringIO
from datetime import datetime

load_dotenv()

def download_csv(ticker, start_date="2023-01-01", end_date=None, save=True):
    headers = {
        "Accept": "text/csv",
        "Authorization": "Token " + os.getenv("TINGO_API_KEY")
    }

    # Use today's date as default end_date
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    url = (
        f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
        f"?startDate={start_date}&endDate={end_date}&format=csv"
    )

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').tz_localize(None)

    if save:
        os.makedirs("data", exist_ok=True)
        filename = f"data/{ticker.upper()}_{start_date}_to_{end_date}.csv"
        df.to_csv(filename)
        print(f"Saved to {filename}")

    return df

__all__ = ['download_csv']

