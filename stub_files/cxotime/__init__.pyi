from __future__ import annotations

from typing import overload, Iterable, Union, Any
from datetime import datetime
from numpy.typing import NDArray
import numpy as np

# --- Types ---
CxoScalar = Union[str, float, datetime]
CxoArray = Union[Iterable[str], Iterable[float], Iterable[datetime]]
CxoTimeLike = Union[CxoScalar, CxoArray, "CxoTime"]


class CxoTime:
    """
    Pylance type stub for cxotime.CxoTime.
    Covers scalar and array-valued operations.
    """

    # === Common scalar attributes ===
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

    # === ndarray versions (vectorized CxoTime) ===
    value: Union[float, NDArray[np.float64]]
    jd1: Union[float, NDArray[np.float64]]
    jd2: Union[float, NDArray[np.float64]]
    mask: Union[bool, NDArray[np.bool_]]

    # === Basic metadata ===
    shape: tuple[int, ...]
    size: int
    ndim: int
    scale: str
    format: str
    precision: int

    # ========================
    # Constructor overloads
    # ========================

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

    # ========================
    # Arithmetic
    # ========================

    def __add__(self, other: Any) -> "CxoTime": ...
    def __sub__(self, other: Any) -> Union["CxoTime", float]: ...

    # ========================
    # Conversion and formatting
    # ========================

    def to_datetime(self) -> Union[datetime, NDArray[Any]]: ...
    def to_string(self, format: str | None = None) -> Union[str, NDArray[Any]]: ...
    def strftime(self, fmt: str) -> str: ...

    # Astropy-like
    def to_value(self, unit: Any = None) -> float: ...

    # ========================
    # Array behavior
    # ========================

    def reshape(self, *shape: int) -> "CxoTime": ...
    def ravel(self) -> "CxoTime": ...
    def flatten(self) -> "CxoTime": ...
    def squeeze(self) -> "CxoTime": ...
    def take(self, idx: int | Iterable[int]) -> "CxoTime": ...

    # numpy-like
    def mean(self) -> float: ...
    def min(self) -> float: ...
    def max(self) -> float: ...
    def ptp(self) -> float: ...
    def sort(self) -> "CxoTime": ...
    def argsort(self) -> NDArray[np.int_]: ...
    def argmin(self) -> int: ...
    def argmax(self) -> int: ...

    # ========================
    # Class methods
    # ========================

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

    # ========================
    # Utilities
    # ========================

    def get_conversions(self) -> dict[str, Any]: ...
    def print_conversions(self, file: Any = ...) -> None: ...
