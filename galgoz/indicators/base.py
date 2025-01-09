import pandas as pd

from typing import Optional
from pydantic import BaseModel, Field


class Indicator(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    """
    Indicator class for representing financial indicators.
    Attributes:
        name (str): The name of the indicator.
        data (pd.Series | pd.DataFrame): The data associated with the indicator, which can be a pandas Series or DataFrame.
        mode (str): Type of plot mode (from plotly.graph_objects). Options are "lines" (default), "markers", "lines+markers", "text", "lines+text", "markers+text", or "lines+markers+text".
        row (int): The subplot row number associated with the indicator. Default is 1 (top row).
        line (Optional[dict]): Optional dictionary containing line information for the indicator.
    """
    name: str = Field(title="Indicator name", description="The name of the indicator.")
    data: Optional[pd.Series | pd.DataFrame] = Field(
        title="Indicator data",
        description="The index must be a Timestamp and the values floats or integers.",
        default=None,
    )
    row: int = Field(
        title="Subplot row number",
        description="The plot can have multiple rows, where row 1 is the main plot, typically a Candlestic plot. Default is 1 (main plot).",
        default=1,
    )
    mode: str = Field(
        title="Plot mode",
        description='Type of plot (from plotly.graph_objects). Options are "lines" (default), "markers", "lines+markers", "text", "lines+text", "markers+text", or "lines+markers+text".',
        default="lines",
    )
    line: dict = Field(
        title="Line information",
        description="Dictionary containing line formatting information. See plotly.graph_objects",
        default=dict(color="blue", width=2),
    )
    marker: dict = Field(
        title="Marker information",
        description="Dictionary containing marker format information. See plotly.graph_objects",
        default=dict(
            size=5,  # Size of the markers
            color="blue",  # Color of the markers
            symbol="circle",
        ),
    )

    output: Optional[pd.Series] = Field(title="Indicator output data", default=None)

    @classmethod
    def validate_output(cls, output: pd.Series) -> pd.Series:
        if not isinstance(output.index, pd.DatetimeIndex):
            raise ValueError("The index of the output must be a pandas DatetimeIndex.")
        if not pd.api.types.is_float_dtype(output):
            raise ValueError("The values of the output must be of float type.")
        return output

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_output
