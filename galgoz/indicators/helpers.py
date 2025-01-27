from ..indicators.base import Indicator
import pandas as pd


class Hline(Indicator):
    yvalue: float = 0
    row: int = 2
    line: dict = dict(color="grey", width=1)

    def __init__(self, data: pd.DataFrame, yvalue: float = yvalue, **kwargs):
        super().__init__(name="hline", data=data)
        self.yvalue = yvalue
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Horizontal Line (yvalue={self.yvalue})"

    def run(self):
        self.output = pd.Series(
            [self.yvalue] * len(self.data), index=self.data.index, name="hline"
        )

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()
