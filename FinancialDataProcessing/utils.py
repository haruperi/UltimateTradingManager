import numpy as np
from typing import Union, Sequence


def to_percent(number: float) -> str:
    """
    Converts a floating-point number to a percentage string.

    Parameters:
        number (float): The number to be converted to a percentage.

    Returns:
        str: The formatted percentage string. If the number is NaN, returns "-".
    """
    if np.isnan(number):
        return "-"
    return format(number, ".2%")


def to_percent_num(number: float) -> str:
    """
    Converts a floating-point number to a percentage string without the '%' sign.

    Parameters:
        number (float): The number to be converted to a percentage.

    Returns:
        str: The formatted percentage string without the '%' sign. If the number is NaN, returns "-".
    """
    if np.isnan(number):
        return "-"
    return format(number * 100, ".2f")


def to_float(number: float, decimals: int = 2) -> str:
    """
    Formatting helper for floats with a specified number of decimals.

    Parameters:
        number (float): The number to format.
        decimals (int): The number of decimal places to format the number to.

    Returns:
        str: The formatted number as a string. If the number is NaN, returns "-".
    """
    if np.isnan(number):
        return "-"
    format_string = f".{decimals}f"
    return format(number, format_string)


def get_freq(period: str) -> Union[str, None]:
    """
    Returns the descriptive name of a given period code.

    Parameters:
        period (str): The period code to be converted to its descriptive name.

    Returns:
        Union[str, None]: The descriptive name of the period code. If the period code is not found, returns None.
    """
    period = period.upper()
    periods = {
        "B": "business day",
        "C": "custom business day",
        "D": "daily",
        "WE": "weekly",
        "ME": "monthly",
        "YE": "Yearly",
        "BM": "business month end",
        "CBM": "custom business month end",
        "MS": "month start",
        "BMS": "business month start",
        "CBMS": "custom business month start",
        "Q": "quarterly",
        "BQ": "business quarter end",
        "QS": "quarter start",
        "BQS": "business quarter start",
        "Y": "yearly",
        "A": "yearly",
        "BA": "business year end",
        "AS": "year start",
        "BAS": "business year start",
        "H": "hourly",
        "T": "minutely",
        "S": "secondly",
        "L": "milliseconds",
        "U": "microseconds",
    }

    return periods.get(period, None)


def scale(val: float, src: Sequence[float], dst: Sequence[float]) -> float:
    """
    Scales a value from a source range to a destination range.
    If the value is outside the bounds of the source range, it is clipped to
    the nearest bound of the destination range.

    Parameters:
        val (float): The value to be scaled.
        src (Sequence[float]): A sequence of two floats representing the source range.
        dst (Sequence[float]): A sequence of two floats representing the destination range.

    Returns:
        float: The value scaled to the destination range.

    Examples:
        >>> scale(0, (0.0, 99.0), (-1.0, 1.0))
        -1.0
        >>> scale(-5, (0.0, 99.0), (-1.0, 1.0))
        -1.0
        >>> scale(50, (0.0, 100.0), (0.0, 1.0))
        0.5
    """
    if val < src[0]:
        return dst[0]
    if val > src[1]:
        return dst[1]

    return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]
