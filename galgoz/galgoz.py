from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Any
from dotenv import load_dotenv
import os
import pandas as pd
import oandapyV20  # type: ignore
import oandapyV20.endpoints.accounts as accounts  # type: ignore
import oandapyV20.endpoints.instruments as instruments  # type: ignore
import plotly.graph_objects as go
from datetime import datetime as dt

load_dotenv()

class Galgoz(BaseModel):
    account: str = "practice"       
    account_id: str = os.getenv(
        "OANDA_LIVE_ACCOUNT_ID" if account == "live" else "OANDA_PRACTICE_ACCOUNT_ID",
        "",
    )
    client: Any = oandapyV20.API(
        access_token=os.getenv(
            "OANDA_LIVE_ACCESS_TOKEN"
            if account == "live"
            else "OANDA_PRACTICE_ACCESS_TOKEN"
        )
    )
    instrument: str = "GBP_JPY"
    

    def fetch_instruments(self, fetch_all_metadata=False):
        instruments = accounts.AccountInstruments(accountID=self.account_id)
        response = self.client.request(instruments)
        instruments = response.get("instruments", [])        
        return instruments

    def fetch_candles(self, granularity="H1", count=10, price="M", date_from=None, date_to=None):
        """
        Fetches candle data for a specified instrument.

        Parameters:
        Consult the OANDA API (https://developer.oanda.com/rest-live-v20/introduction/) documentation for the available parameters:
        - granularity (str): The time frame for each candle (e.g., "H1" for 1 hour). Default is "H1".
        - count (int): The number of candles to fetch if date_from and date_to are not specified. Default is 10.
        - price (str): The price type to fetch (e.g., "M" for mid price). Default is "M".
        - date_from (datetime): The start date and time for the candle data in UTC. Default is None.
        - date_to (datetime): The end date and time for the candle data in UTC. Default is None.

        Returns:
        - list: A list of candle data dictionaries.

        If both date_from and date_to are provided, the method fetches candles within the specified date range.
        Otherwise, it fetches the specified count of candles.
        """
        params = {
            "granularity": granularity,
            "price": price,
        }

        if date_from is not None and date_to is not None:
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            params["from"] = dt.strftime(date_from, date_format)
            params["to"] = dt.strftime(date_to, date_format)
        else:
            params["count"] = count

        candles = instruments.InstrumentsCandles(
            instrument=self.instrument, params=params
        )
        response = self.client.request(candles)

        return response.get("candles", [])
    
    def candles_df(self, **kwargs):
        """
        Fetches candle data and returns it as a pandas DataFrame.

        Parameters:
        **kwargs: Check the `fetch_candles` method for the available parameters.

        Returns:
        pd.DataFrame: A DataFrame containing the candle data with columns 'time', 'volume', and price-specific columns.
        """
        price_key = self._set_price_string(kwargs)
        data = self.fetch_candles(**kwargs)
        data_dicts = [{'time': item['time'], 'volume': item['volume'], **item[price_key]} for item in data]
        df = pd.DataFrame(data_dicts)
        return df

    def _set_price_string(self, kwargs):
        """ 
        Helper method to check the price type and set the corresponding price key.
        """
        if 'price' not in kwargs:
            kwargs['price'] = 'M'
            price_key = 'mid'
        elif kwargs['price'] == 'M':
            price_key = 'mid'
        elif kwargs['price'] == 'A':
            price_key = 'ask'
        elif kwargs['price'] == 'B':
            price_key = 'bid'
        else:
            kwargs['price'] = 'M'
            price_key = 'mid'
            print("Invalid price type provided. Defaulting to 'M'. Accepted values are 'M', 'A', 'B'.")
        return price_key


