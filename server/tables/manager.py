"""Table manager for tracking all active tables."""

from typing import TYPE_CHECKING, Any
import uuid

from .table import Table

if TYPE_CHECKING:
    from ..users.base import User


class TableManager:
    """Manages all active tables on the server."""

    def __init__(self):
        self._tables: dict[str, Table] = {}
        self._username_to_table: dict[str, str] = {}  # username -> table_id O(1) lookup
        self._server: Any = None  # Reference to server for destroy/save notifications

    def create_table(
        self,
        game_type: str,
        host_username: str,
        host_user: "User",
    ) -> Table:
        """Create a new table."""
        table_id = str(uuid.uuid4())[:8]
        while table_id in self._tables:
            table_id = str(uuid.uuid4())[:8]
        table = Table(
            table_id=table_id,
            game_type=game_type,
            host=host_username,
        )
        table._manager = self
        table._server = self._server
        if self._server:
            table._db = self._server._db
        table.add_member(host_username, host_user, as_spectator=False)
        self._tables[table_id] = table
        if self._server and hasattr(self._server, "on_tables_changed"):
            self._server.on_tables_changed()
        return table

    def get_table(self, table_id: str) -> Table | None:
        """Get a table by ID."""
        return self._tables.get(table_id)

    def remove_table(self, table_id: str) -> None:
        """Remove a table."""
        table = self._tables.pop(table_id, None)
        if table:
            for member in table.members:
                self._username_to_table.pop(member.username, None)
            if self._server and hasattr(self._server, "on_tables_changed"):
                self._server.on_tables_changed()

    def get_all_tables(self) -> list[Table]:
        """Get all tables."""
        return list(self._tables.values())

    def get_tables_by_type(self, game_type: str) -> list[Table]:
        """Get all tables of a specific game type."""
        return [t for t in self._tables.values() if t.game_type == game_type]

    def get_waiting_tables(self, game_type: str | None = None) -> list[Table]:
        """Get all tables in waiting status."""
        tables = self._tables.values()
        if game_type:
            tables = [t for t in tables if t.game_type == game_type]
        return [t for t in tables if t.status == "waiting"]

    def find_user_table(self, username: str) -> Table | None:
        """Find the table a user is currently in (O(1) via reverse-lookup dict)."""
        table_id = self._username_to_table.get(username)
        if table_id:
            return self._tables.get(table_id)
        return None

    def on_tick(self) -> None:
        """Tick all active tables."""
        for table in list(self._tables.values()):
            table.on_tick()

    def add_table(self, table: Table) -> None:
        """Add an existing table (e.g., loaded from database)."""
        table._manager = self
        table._server = self._server
        if self._server:
            table._db = self._server._db
        self._tables[table.table_id] = table
        for member in table.members:
            self._username_to_table[member.username] = table.table_id

    def save_all(self) -> list[Table]:
        """Save all tables' game state and return them."""
        for table in self._tables.values():
            table.save_game_state()
        return list(self._tables.values())

    def on_table_destroy(self, table: Table) -> None:
        """Handle table destruction. Called by Table.destroy()."""
        self.remove_table(table.table_id)
        if self._server:
            self._server.on_table_destroy(table)
