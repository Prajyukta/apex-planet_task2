"""Small, safe database access layer for SQLAlchemy and pandas."""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

import pandas as pd
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import Connection

from .config import Settings, get_settings


class DatabaseManager:
    """Own an SQLAlchemy engine and expose parameterized query helpers."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        self.engine: Engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        """Yield a connection and return it to the pool after use."""
        with self.engine.begin() as connection:
            yield connection

    def execute_query(
        self, query: str, params: Mapping[str, Any] | None = None
    ) -> int:
        """Execute a statement with bound parameters; return affected row count."""
        with self.engine.begin() as connection:
            result = connection.execute(text(query), params or {})
            return result.rowcount

    def query_to_df(
        self, query: str, params: Mapping[str, Any] | None = None
    ) -> pd.DataFrame:
        """Load a SELECT statement into a DataFrame using bound parameters."""
        return pd.read_sql(text(query), self.engine, params=params or {})

    def close(self) -> None:
        self.engine.dispose()
