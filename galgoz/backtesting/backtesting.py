from pydantic import BaseModel
from pathlib import Path
import pandas as pd
from typing import Optional
from galgoz.indicators import *

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_FOLDER = ROOT_DIR / "data"


class Backtesting(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    strategy: str = "Galgoz Strategy"
    instrument: str = "GBP_JPY"
    timeframe: str = "H1"
    init_rows: int = 250
    data: pd.DataFrame = pd.DataFrame()
    df_bt: pd.DataFrame = pd.DataFrame()

    def __init__(self, **data):
        super().__init__(**data)
        self.get_data()
        self.df_bt = self.data.head(self.init_rows).copy()

    def __str__(self):
        return f"Backtesting {self.strategy} on {self.instrument} from {self.start_date} to {self.end_date}"

    def __repr__(self):
        return f"Backtesting(strategy={self.strategy}, instrument={self.instrument}, timeframe={self.timeframe}, start_date={self.start_date}, end_date={self.end_date})"

    def get_data(self):
        self.data = pd.read_pickle(
            DATA_FOLDER / f"{self.instrument}_{self.timeframe}.pkl"
        )
        self.data["time"] = pd.to_datetime(self.data["time"])
        self.data["time_str"] = self.data["time"].dt.strftime(" %-b %d, '%y %H:%M")
        self.data.set_index("time", inplace=True)


if __name__ == "__main__":
    bt = Backtesting()
    # print(bt.df_bt.head())
    sg = SG(data=bt.df_bt["mid_c"]).output
    print(sg.head())
