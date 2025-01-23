from .indicators.base import Indicator


def generate_indicators(*indicators: Indicator):
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
