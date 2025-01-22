from pydantic import BaseModel, ConfigDict
from typing import Any, List, Optional
from dotenv import load_dotenv
import os
import pandas as pd
import oandapyV20  # type: ignore
import oandapyV20.endpoints.accounts as accounts  # type: ignore
import oandapyV20.endpoints.instruments as instruments  # type: ignore
import oandapyV20.endpoints.orders as orders  # type: ignore
import oandapyV20.endpoints.trades as trades  # type: ignore
from oandapyV20.exceptions import V20Error  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from galgoz.plotting.candles import plot as cplot
from galgoz.indicators.base import Indicator

# Load env parameters (account details and tokens)
load_dotenv()

# Get the root directory of the project
ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_FOLDER = ROOT_DIR / "data"

MAX_CANDLES = 5000

# Time increments for each granularity in minutes
TIME_INCREMENT = {
    "M1": 1 * MAX_CANDLES,
    "M5": 5 * MAX_CANDLES,
    "M15": 15 * MAX_CANDLES,
    "M30": 30 * MAX_CANDLES,
    "H1": 60 * MAX_CANDLES,
    "H4": 240 * MAX_CANDLES,
    "D": 1440 * MAX_CANDLES,
    "W": 10080 * MAX_CANDLES,
    "M": 43200 * MAX_CANDLES,
}


class Galgoz(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    fig: Optional[go.Figure] = None

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
        print(response)
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
            self._validate_date_format(date_from, date_to)

            start_date = dt.strptime(date_from, "%Y-%m-%dT%H:%M:%SZ")
            end_date = start_date

            candles_list: list = []
            while end_date < dt.strptime(date_to, "%Y-%m-%dT%H:%M:%SZ"):
                end_date = start_date + timedelta(minutes=TIME_INCREMENT[granularity])
                params["from"] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

                if end_date > dt.strptime(date_to, "%Y-%m-%dT%H:%M:%SZ"):
                    end_date = dt.strptime(date_to, "%Y-%m-%dT%H:%M:%SZ")

                params["to"] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                print(f"Fetching candles from {start_date} to {end_date}")
                candles = instruments.InstrumentsCandles(
                    instrument=self.instrument, params=params
                )
                response = self.client.request(candles)
                candles_list.extend(response.get("candles", []))
                print(f"Total candles fetched: {len(response.get('candles', []))}")
                start_date = end_date
            return candles_list
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

    def _validate_date_format(self, date_from, date_to):
        try:
            dt.strptime(date_from, "%Y-%m-%dT%H:%M:%SZ")
            dt.strptime(date_to, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DDTHH:MM:SSZ")

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
        # Convert columns to float
        float_columns = [col for col in df.columns if col not in ["time", "complete"]]
        df[float_columns] = df[float_columns].astype(float)
        df["complete"] = df["complete"].astype(int)
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
        try:
            response = self.client.request(r)
            print("Order created successfully.")
        except V20Error as e:
            print(f"V20Error: {e}")
            response = None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            response = None
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
        try:
            response = self.client.request(r)
            print("Trade closed successfully.")
        except V20Error as e:
            print(f"V20Error: {e}")
            response = None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            response = None
        return response

    #    def indicators(self, data: pd.DataFrame, indicators: dict) -> pd.DataFrame:

    def store_data(
        self,
        granularity: str = "H1",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        **kwargs,
    ):
        """
        Fetches candle data and stores it as a pickle file in the data folder.

        The filename is generated based on the instrument, granularity, date_from, date_to, and the current timestamp.

        Args:
            granularity (str): The time frame for each candle (e.g., "H1" for 1 hour). Default is "H1".
            date_from (str): The start date and time for the candle data in UTC. Date format must be YYYY-MM-DDTHH:MM:SSZ. Default is None.
            date_to (str): The end date and time for the candle data in UTC. Date format must be YYYY-MM-DDTHH:MM:SSZ. Default is None.

        Returns:
            str: The path to the saved pickle file.
        """
        if date_from is None or date_to is None:
            raise ValueError("Both date_from and date_to must be provided.")

        df = self.candles_df(
            granularity=granularity, date_from=date_from, date_to=date_to, **kwargs
        )
        filename = f"{self.instrument}_{granularity}.pkl"
        filepath = DATA_FOLDER / filename
        if len(df) > 0:
            df.to_pickle(filepath)
            print(f"Data saved to {filepath}")
        else:
            print(
                f"No data to save for {self.instrument} at {granularity} granularity."
            )

    def generate_indicators_list(self, *indicators: Indicator):
        """
        Generates a list of indicators with plotting metadata.

        Args:
            *indicators: Variable length argument list of Indicator types.

        Returns:
            list: A list of dictionaries, each containing the attributes and plotting metadata.
        """
        indicators_list = []
        for indicator in indicators:
            indicators_list.append(
                {
                    "name": indicator.name,
                    "data": indicator.output,
                    "mode": indicator.mode,
                    "row": indicator.row,
                    "line": indicator.line,
                    "marker": indicator.marker,
                }
            )
        return indicators_list

    def plot_candles(
        self,
        df: Optional[pd.DataFrame] = None,
        indicators: Optional[List] = None,
        show: bool = True,
        **kwargs,
    ) -> go.Figure:
        """
        Plots candlestick chart using the provided DataFrame.
        This function utilizes the `galgoz.plotting.candles.plot` method to generate
        a candlestick chart from the given DataFrame.
        Args:
            df (Optional[pd.DataFrame]): The DataFrame containing the data to plot.
                If None, the function will use a default DataFrame.
            **kwargs: Additional keyword arguments to pass to `galgoz.plotting.candles.plot`.
        Returns:
            go.Figure: The plotly figure object containing the candlestick chart.
        """
        self.fig = cplot(df=df, indicators=indicators, **kwargs)
        if show:
            self.fig.show()
        return self.fig
