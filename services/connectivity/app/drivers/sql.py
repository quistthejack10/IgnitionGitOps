"""SQL database driver (PRD FR-C5).

M3: PostgreSQL, SQL Server, MySQL/MariaDB (Oracle/ODBC P1). Polled query source with
watermark/change-tracking column, one-shot query node, insert/update/upsert sink, stored-proc
call. Connection pooling and per-connection read-only enforcement. Built on SQLAlchemy/ODBC.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from forge_common.events import Event

from app.base import Connection, Sink, Source


class SqlConnection(Connection):
    async def connect(self) -> None:
        raise NotImplementedError("SQL connect/pool (M3)")

    async def test(self) -> bool:
        raise NotImplementedError("SQL test-before-save (M3)")


class SqlPolledSource(Source):
    async def stream(self) -> AsyncIterator[Event]:
        raise NotImplementedError("SQL watermark-polled source (M3)")
        yield  # pragma: no cover


class SqlSink(Sink):
    async def write(self, event: Event) -> None:
        raise NotImplementedError("SQL insert/update/upsert sink (M3)")
