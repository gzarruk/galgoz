from typing import List
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd
import numpy as np
from . import DATA_FOLDER
from .utils import set_data_index_and_time_str
from .indicators import Indicator, SG, WPR
import time


class Backtest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    strategy: str = Field(
        title="Strategy name",
        default="Galgoz Standard",
    )
    data: pd.DataFrame = Field(
        title="Dataframe with OHLCV data",
        description="The dataframe must have the following columns: 'volume', 'mid_o', 'mid_h', 'mid_l', 'mid_c', 'time'. The time column must be a time string. If no data is provided, GBP_JPY in the H1 timeframe from the data folder is loaded.",
        default=pd.DataFrame(),
    )
    indicators: List[Indicator] = Field(
        title="List of indicators",
        description="List of indicators to be used in the backtest",
        default=[],
    )
    init_rows: int = Field(
        title="Number of initial rows to initlize",
        description="Backtesting is done recursevely, i.e. one time-step at a time. Thefore, during the initialization phase, the model needs to be initialized with a certain number of rows. This is the number of rows to initialize.",
        default=500,
    )

    def __str__(self):
        return f"Backtest for {self.strategy} with the indicators: {self.indicators}"

    def __init__(self, **data):
        super().__init__(**data)
        print(f"Initializing backtest for {self.strategy}")
        if len(self.data) == 0:
            # Load GBP_JPY_H1.pkl file from DATA_FOLDER
            self.data = pd.read_pickle(DATA_FOLDER / "GBP_JPY_H1.pkl")
        set_data_index_and_time_str(self.data)
        if len(self.indicators) == 0:
            print(
                "No indicators provided. Using default indicators: Savitzky-Golay filter and Williams %R"
            )
            self.indicators = [
                SG(data=self.data.iloc[: self.init_rows]),
                WPR(data=self.data.iloc[: self.init_rows]),
            ]
        # Create columns for the indicators, signals, entry price, sl and tp and insert the initial values as NaNs
        for indicator in self.indicators:
            self.data[indicator.name] = indicator.output
        self.data.insert(
            len(self.data.columns), "signals", np.nan, allow_duplicates=False
        )
        self.data.insert(
            len(self.data.columns), "entry", np.nan, allow_duplicates=False
        )
        self.data.insert(
            len(self.data.columns), "stop_loss", np.nan, allow_duplicates=False
        )
        self.data.insert(
            len(self.data.columns), "take_profit", np.nan, allow_duplicates=False
        )

    def run(self):
        start_time = time.time()
        if len(self.data) == 0:
            print("No data provided for backtest")
            return None
        print(f"Running backtest on {self.strategy}")
        for i in range(self.init_rows, len(self.data)):
            data_slice = self.data.iloc[: i + 1]
            # Update indicators and main DataFrame for each time-step
            for indicator in self.indicators:
                indicator.update(data_slice)
                last_output = indicator.output.iloc[-1]
                self.data.at[self.data.index[i], indicator.name] = last_output
        print(
            f"Backtest completed in {time.time()-start_time:.2f} seconds and evaluated {len(self.data)-self.init_rows} time-steps"
        )
