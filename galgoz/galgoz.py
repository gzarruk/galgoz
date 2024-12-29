from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Any, Optional
from dotenv import load_dotenv
import os
import pandas as pd
import oandapyV20  # type: ignore
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import plotly.graph_objects as go
from datetime import datetime as dt
from pathlib import Path

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parents[1]

# Define the path to the data folder
DATA_FOLDER = ROOT_DIR / "data"
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

    def fetch_instruments(self):
        """
        Fetches the list of instruments for the account.

        This method sends a request to retrieve the instruments associated with the account ID
        and returns the list of instruments.

        Returns:
            list: A list of instruments associated with the account.
        """

        instruments = accounts.AccountInstruments(accountID=self.account_id)
        response = self.client.request(instruments)
        instruments = response.get("instruments", [])
        return instruments

    def fetch_candles(
        self,
        granularity: str = "H1",
        count: int = 10,
        price: str = "MBA",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list:
        """
        Fetches candle data for a specified instrument.

        Args:
            granularity (str): The time frame for each candle (e.g., "H1" for 1 hour). Default is "H1".
            count (int): The number of candles to fetch if date_from and date_to are not specified. Default is 10.
            price (str): The price type to fetch (e.g., "M" for mid price). Default is "M".
            date_from (str): The start date and time for the candle data in UTC. Date format must be YYYY-MM-DDTHH:MM:SSZ. Default is None.
            date_to (str): The end date and time for the candle data in UTC.Date format must be YYYY-MM-DDTHH:MM:SSZ. Default is None.

        Returns:
            list: A list of candle data dictionaries.

        If both date_from and date_to are provided, the method fetches candles within the specified date range.
        Otherwise, it fetches the specified count of candles.
        """
        params = {
            "granularity": granularity,
            "price": price,
        }

        if date_from is not None and date_to is not None:
            try:
                dt.strptime(date_from, "%Y-%m-%dT%H:%M:%SZ")
                dt.strptime(date_to, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError(
                    "Incorrect date format, should be YYYY-MM-DDTHH:MM:SSZ"
                )

            params["from"] = date_from
            params["to"] = date_to
        else:
            if count > 5000:
                count = 5000
                print(
                    "The maximum number of candles that can be fetched is 5000. Setting count to 5000."
                )
            params["count"] = str(count)

        candles = instruments.InstrumentsCandles(
            instrument=self.instrument, params=params
        )
        response = self.client.request(candles)

        return response.get("candles", [])

    def candles_df(self, **kwargs) -> pd.DataFrame:
        """
        Fetches candle data and returns it as a pandas DataFrame.

        Args:
            **kwargs: Check the `fetch_candles` method for the available parameters.

        Returns:
            pd.DataFrame: A DataFrame containing the candle data with columns 'time', 'volume', and price-specific columns.
        """
        data = self.fetch_candles(**kwargs)
        df = pd.json_normalize(data, sep="_")
        df.columns = df.columns.str.replace("bid_", "bid_", regex=False)
        df.columns = df.columns.str.replace("ask_", "ask_", regex=False)
        df.columns = df.columns.str.replace("mid_", "mid_", regex=False)
        return df

    def create_order(self, units: str, type: str = "MARKET"):
        """
        Creates an order with the specified units and type.

        Args:
            units (str): The number of units to order.
            type (str, optional): The type of order to create. Defaults to "MARKET".

        Returns:
            dict: The response from the order creation request.
        """

        data = {
            "order": {
                "instrument": self.instrument,
                "units": units,
                "timeInForce": "FOK",
                "type": type,
                "positionFill": "DEFAULT",
            }
        }

        r = orders.OrderCreate(accountID=self.account_id, data=data)
        response = self.client.request(r)
        return response

    def close_trade(self, trade_id: str, units: str = "ALL"):
        """
        Close a specific trade by its trade ID.

        Args:
            trade_id (str): The ID of the trade to close.
            units (str): The number of units to close. Default is "ALL".

        Returns:
            dict: The response from the OANDA API.
        """
        data = {"units": units}

        r = trades.TradeClose(accountID=self.account_id, tradeID=trade_id, data=data)
        response = self.client.request(r)
        return response

    def store_data(self):
        pass
