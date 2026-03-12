from __future__ import annotations

from typing import overload, Iterable, Union, Any
from datetime import datetime
from numpy.typing import NDArray
import numpy as np

class CxoTimeDescriptor:
    """Descriptor that exposes attributes for different formats."""
    def __get__(self, instance: Any, owner: Any) -> Any: ...
    def __set__(self, instance: Any, value: Any) -> None: ...


# Alias matches what the module exports
CxoTimeLike = Union[
    str,
    float,
    datetime,
    Iterable[str],
    Iterable[float],
    Iterable[datetime],
    "CxoTime",
]


class CxoTime:
    """
    Typed stub for cxotime.CxoTime.
    """

    # ---- Scalar attributes ----
    secs: float
    cxcsec: float
    date: str
    iso: str
    isot: str
    yday: str
    decimalyear: float
    unix: float
    mjd: float
    jd: float
    jyear: float
    byear: float

    # ---- Vector forms ----
    value: Union[float, NDArray[np.float64]]
    jd1: Union[float, NDArray[np.float64]]
    jd2: Union[float, NDArray[np.float64]]
    mask: Union[bool, NDArray[np.bool_]]

    shape: tuple[int, ...]
    size: int
    ndim: int
    scale: str
    format: str
    precision: int

    # ---- Constructors ----
    @overload
    def __init__(self, t: None = ..., **kwargs): ...
    @overload
    def __init__(self, t: float, **kwargs): ...
    @overload
    def __init__(self, t: str, **kwargs): ...
    @overload
    def __init__(self, t: datetime, **kwargs): ...
    @overload
    def __init__(self, t: Iterable[float], **kwargs): ...
    @overload
    def __init__(self, t: Iterable[str], **kwargs): ...
    @overload
    def __init__(self, t: Iterable[datetime], **kwargs): ...
    @overload
    def __init__(self, t: "CxoTime", **kwargs): ...

    # ---- Arithmetic ----
    def __add__(self, other: Any) -> "CxoTime": ...
    def __sub__(self, other: Any) -> Union["CxoTime", float]: ...

    # ---- Utilities ----
    def to_datetime(self) -> Union[datetime, NDArray[Any]]: ...
    def to_string(self, format: str | None = None) -> Union[str, NDArray[Any]]: ...
    def strftime(self, fmt: str) -> str: ...
    def to_value(self, unit: Any = None) -> float: ...
    def get_conversions(self) -> dict[str, Any]: ...
    def print_conversions(self, file: Any = ...) -> None: ...

    # ---- Array-like behavior ----
    def reshape(self, *shape: int) -> "CxoTime": ...
    def ravel(self) -> "CxoTime": ...
    def flatten(self) -> "CxoTime": ...
    def squeeze(self) -> "CxoTime": ...
    def take(self, idx: int | Iterable[int]) -> "CxoTime": ...

    def mean(self) -> float: ...
    def min(self) -> float: ...
    def max(self) -> float: ...
    def ptp(self) -> float: ...
    def sort(self) -> "CxoTime": ...
    def argsort(self) -> NDArray[np.int_]: ...
    def argmin(self) -> int: ...
    def argmax(self) -> int: ...

    # ---- Class methods ----
    @classmethod
    def now(cls) -> "CxoTime": ...

    @classmethod
    def linspace(
        cls,
        start: CxoTimeLike,
        stop: CxoTimeLike,
        num: int | None = None,
        step_max: Any | None = None,
    ) -> "CxoTime": ...
