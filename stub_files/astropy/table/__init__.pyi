from __future__ import annotations

from typing import Any, Iterable, Iterator, Mapping, Sequence, overload, Literal, Union
from datetime import datetime
from numpy.typing import NDArray
import numpy as np

# -------------------------------
# Column types
# -------------------------------

class Column:
    """Array-like table column."""
    name: str
    dtype: Any
    shape: tuple[int, ...]
    unit: Any | None
    format: str | None
    description: str | None
    meta: dict[str, Any]
    mask: NDArray[np.bool_] | bool
    data: NDArray[Any]  # backing array (may be a mixin at runtime)

    # Common array-like operations
    def copy(self, copy_data: bool = ...) -> Column: ...
    def astype(self, dtype: Any, *, copy: bool = ...) -> Column: ...
    def to_list(self) -> list[Any]: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Any]: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class MaskedColumn(Column):
    """Masked variant of Column."""
    # In practice, inherits behavior; mask is required/propagated.
    masked: bool

# -------------------------------
# Row view
# -------------------------------

class Row:
    """A single row view into a Table."""
    table: Table
    index: int

    def as_void(self) -> Any: ...
    def as_tuple(self) -> tuple[Any, ...]: ...
    def __getitem__(self, key: int | str) -> Any: ...
    def __iter__(self) -> Iterator[Any]: ...

# -------------------------------
# Grouping
# -------------------------------

class TableGroupBy:
    """Group-by result helper for grouped tables (aggregation, filtering)."""
    # Minimal surface for aggregation pipelines:
    def aggregate(self, func: Any) -> Table: ...
    def filter(self, func: Any) -> Table: ...
    def apply(self, func: Any) -> Table: ...

class TableGroups:
    """A Table decorated with group metadata."""
    parent_table: Table
    keys: Sequence[str] | None

    @property
    def groups(self) -> TableGroupBy: ...

# -------------------------------
# Core Table types
# -------------------------------

_T = Union["Table", "QTable"]

class _BaseTable:
    """Common typed surface shared by Table and QTable."""
    # Column and metadata access
    columns: Mapping[str, Column]
    colnames: list[str]
    meta: dict[str, Any]

    # Shape-like information
    masked: bool
    # Note: Table is ragged at runtime only if column lengths mismatch (not allowed),
    # so we keep simple row-based API:
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Row]: ...
    def iterrows(self) -> Iterator[Row]: ...

    # Construction helpers
    def copy(self, copy_data: bool = ...) -> _T: ...
    def add_row(self, vals: Mapping[str, Any] | Sequence[Any] | None = ..., *, index: int | None = ...) -> None: ...
    def add_rows(self, rows: Iterable[Mapping[str, Any] | Sequence[Any]]) -> None: ...
    def remove_row(self, index: int) -> None: ...
    def remove_rows(self, indices: Sequence[int]) -> None: ...
    def add_column(self, col: Column | Any, name: str | None = ..., index: int | None = ...) -> None: ...
    def add_columns(self, cols: Sequence[Column | Any]) -> None: ...
    def remove_column(self, name: str) -> None: ...
    def remove_columns(self, names: Sequence[str]) -> None: ...
    def rename_column(self, old: str, new: str) -> None: ...
    def rename_columns(self, mapping: Mapping[str, str]) -> None: ...

    # Column lookup
    def __getitem__(self, key: str | Sequence[str]) -> Column | _T: ...
    def __setitem__(self, key: str, value: Any) -> None: ...

    # Grouping
    def group_by(self, keys: str | Sequence[str]) -> TableGroups: ...

    # Pandas interop (typed as Any to avoid pandas dependency)
    def to_pandas(self) -> Any: ...
    @classmethod
    def from_pandas(cls, df: Any) -> _T: ...

    # I/O
    def write(
        self,
        filename: str | Any,
        format: str | None = ...,
        overwrite: bool = ...,
        **kwargs: Any,
    ) -> None: ...

    @classmethod
    def read(
        cls,
        filename: str | Any,
        format: str | None = ...,
        **kwargs: Any,
    ) -> _T: ...

class Table(_BaseTable):
    """Astropy Table with general (non-quantity) columns."""

    @overload
    def __init__(
        self,
        data: Mapping[str, Any] | Sequence[Any] | None = ...,
        *,
        names: Sequence[str] | None = ...,
        dtype: Sequence[Any] | Any | None = ...,
        meta: Mapping[str, Any] | None = ...,
        copy: bool = ...,
        masked: bool = ...,
        rows: Sequence[Sequence[Any]] | None = ...,
    ) -> None: ...
    @overload
    def __init__(self, **kwargs: Any) -> None: ...

class QTable(Table):
    """Astropy Table that preserves Quantity columns."""

# -------------------------------
# Top-level helpers
# -------------------------------

def vstack(
    tables: Sequence[_T],
    *,
    join_type: Literal["outer", "inner", "exact", "strict"] = ...,
    metadata_conflicts: Literal["silent", "warn", "error"] = ...,
    **kwargs: Any,
) -> _T: ...

def hstack(
    tables: Sequence[_T],
    *,
    join_type: Literal["outer", "inner", "exact", "strict"] = ...,
    uniq_col_name: str | None = ...,
    table_names: Sequence[str] | None = ...,
    metadata_conflicts: Literal["silent", "warn", "error"] = ...,
    **kwargs: Any,
) -> _T: ...

def join(
    left: _T,
    right: _T,
    keys: str | Sequence[str] | None = ...,
    *,
    join_type: Literal["inner", "outer", "left", "right"] = ...,
    table_names: tuple[str, str] | None = ...,
    uniq_col_name: str | None = ...,
    metadata_conflicts: Literal["silent", "warn", "error"] = ...,
    **kwargs: Any,
) -> _T: ...

def unique(
    table: _T,
    keys: str | Sequence[str] | None = ...,
    *,
    keep: Literal["first", "last", "none", "all"] = ...,
) -> _T: ...