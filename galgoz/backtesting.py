from typing import List
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd
import numpy as np
from . import DATA_FOLDER
from .utils import set_data_index_and_time_str
from .indicators import Indicator, HMA, MFI
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
    recursive: bool = Field(
        title="Recursive backtest",
        description="If True, the backtest is done recursively, i.e. one time-step at a time. If False, the backtest is done in batch.",
        default=True,
    )

    def __str__(self):
        return f"Backtest for {self.strategy} with the indicators: {self.indicators}"

    def __init__(self, **data):
        super().__init__(**data)
        print(f"Initializing backtest for {self.strategy}")
        if len(self.data) == 0:
            # Load GBP_JPY_H1.pkl file from DATA_FOLDER
            self.data = pd.read_pickle(DATA_FOLDER / "GBP_JPY_H1.pkl").iloc[-5000:]
        set_data_index_and_time_str(self.data)
        if len(self.indicators) == 0:
            print(
                "No indicators provided. Using default indicators: Savitzky-Golay filter and Williams %R.\n---"
            )
            self.indicators = [
                HMA(data=self.data.iloc[: self.init_rows]),
                MFI(data=self.data.iloc[: self.init_rows], window=11),
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

    def entry(self, row: int):
        """
        Method to generate signals based on the indicators. Backtest is provided with a list of default indicators. A default strategy (Galgoz Standard) is used is used to generate entries if none is provided.

        The entry logic is applied stepwise, i.e. for each row of the dataframe. BUY signal are represented by 1 and SELL signals by -1. No signal is represented by 0.

        Galgoz Standard Entries:
        """
        # BUY Signals
        if self.data["HMA"].iloc[row] - self.data["HMA"].iloc[row - 1] > 0:
            if self.data["MFI"].iloc[row] < 25 and self.data["MFI"].iloc[row - 1] > 25:
                return 1
        elif self.data["HMA"].iloc[row] - self.data["HMA"].iloc[row - 1] < 0:
            if self.data["MFI"].iloc[row] > 75 and self.data["MFI"].iloc[row - 1] < 75:
                return -1
        else:
            return 0

    def exit(self, row: int):
        """
        Method to generate exit signals based on the indicators. Backtest is provided with a list of default indicators. A default strategy (Galgoz Standard) is used is used to generate entries if none is provided.

        The exit logic is applied stepwise, i.e. for each row of the dataframe. BUY signal are represented by 1 and SELL signals by -1. No signal is represented by 0.

        Galgoz Standard Exits:
        TO BE IMPLEMENTED
        """
        pass

    def run(self):
        start_time = time.time()
        if len(self.data) == 0:
            print("No data provided for backtest\n---")
            return None
        print(f"Running backtest on {self.strategy}\n---")
        for i in range(self.init_rows, len(self.data)):
            data_slice = self.data.iloc[: i + 1]
            # Update indicators and main DataFrame for each time-step
            for indicator in self.indicators:
                indicator.update(data_slice)
                last_output = indicator.output.iloc[-1]
                self.data.at[self.data.index[i], indicator.name] = last_output
            # Generate signals
            self.data.at[self.data.index[i], "signals"] = self.entry(i)
        if self.data["signals"].isna().all():
            print("No signals were generated during the backtest.\n---")
        else:
            print(f"BUY signals generated: {len(self.data[self.data['signals'] == 1])}")
            print(
                f"SELL signals generated: {len(self.data[self.data['signals'] == -1])}"
            )
        print(
            f"Backtest completed in {time.time()-start_time:.2f} seconds and evaluated {len(self.data)-self.init_rows} time-steps"
        )
