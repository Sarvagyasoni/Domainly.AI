import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.models.conversation import Conversation, Message


class ConversationRepository:
    """Persist conversations and messages in SQLite."""

    DATABASE = Path(__file__).resolve().parent.parent / "storage" / "domainly.db"
    LEGACY_DATABASE = (
        Path(__file__).resolve().parent.parent / "storage" / "conversations.json"
    )

    def __init__(self, database: Path | None = None):
        self.database = database or self.DATABASE
        self.legacy_database = self.LEGACY_DATABASE if database is None else None
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()
        self._migrate_legacy_json()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    summary TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_domain_updated
                    ON conversations(domain, updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp
                    ON messages(conversation_id, timestamp, id);
                """
            )

    def _migrate_legacy_json(self) -> None:
        """Import the previous JSON store once when SQLite is empty."""
        if self.legacy_database is None or not self.legacy_database.exists():
            return
        with self._connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM conversations"
            ).fetchone()[0]
            if count:
                return
            try:
                records = json.loads(
                    self.legacy_database.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                return

            for record in records:
                created_at = record.get("created_at", self._now())
                updated_at = record.get("updated_at", created_at)
                connection.execute(
                    """
                    INSERT OR IGNORE INTO conversations
                        (id, title, domain, summary, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["id"],
                        record.get("title", "New Chat"),
                        record["domain"],
                        record.get("summary"),
                        created_at,
                        updated_at,
                    ),
                )
                for message in record.get("messages", []):
                    connection.execute(
                        """
                        INSERT INTO messages
                            (conversation_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            record["id"],
                            message["role"],
                            message["content"],
                            message.get("timestamp", created_at),
                        ),
                    )

    def _to_conversation(
        self,
        row: sqlite3.Row,
        connection: sqlite3.Connection,
    ) -> Conversation:
        message_rows = connection.execute(
            """
            SELECT role, content, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (row["id"],),
        ).fetchall()
        return Conversation(
            id=row["id"],
            title=row["title"],
            domain=row["domain"],
            summary=row["summary"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            messages=[Message(**dict(message)) for message in message_rows],
        )

    def create(self, domain: str) -> Conversation:
        conversation_id = str(uuid.uuid4())
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations
                    (id, title, domain, summary, created_at, updated_at)
                VALUES (?, 'New Chat', ?, NULL, ?, ?)
                """,
                (conversation_id, domain, now, now),
            )
        return self.get_by_id(conversation_id)  # type: ignore[return-value]

    def get_all(self, domain: str | None = None) -> list[Conversation]:
        query = "SELECT * FROM conversations"
        parameters: tuple[str, ...] = ()
        if domain:
            query += " WHERE domain = ?"
            parameters = (domain,)
        query += " ORDER BY updated_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
            return [self._to_conversation(row, connection) for row in rows]

    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            return self._to_conversation(row, connection) if row else None

    def update(self, conversation: Conversation) -> Conversation:
        now = self._now()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE conversations
                SET title = ?, domain = ?, summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    conversation.title,
                    conversation.domain,
                    conversation.summary,
                    now,
                    conversation.id,
                ),
            )
            if cursor.rowcount == 0:
                raise ValueError("Conversation not found.")
        return self.get_by_id(conversation.id)  # type: ignore[return-value]

    def delete(self, conversation_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,),
            )
            return cursor.rowcount > 0

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> Conversation:
        now = self._now()
        with self._connect() as connection:
            conversation = connection.execute(
                "SELECT title FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if conversation is None:
                raise ValueError("Conversation not found.")

            connection.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, role, content, now),
            )
            if role == "user" and conversation["title"] == "New Chat":
                title = content.strip().replace("\n", " ")[:60] or "New Chat"
                connection.execute(
                    """
                    UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?
                    """,
                    (title, now, conversation_id),
                )
            else:
                connection.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (now, conversation_id),
                )
        return self.get_by_id(conversation_id)  # type: ignore[return-value]

    def get_by_domain(self, domain: str) -> list[Conversation]:
        return self.get_all(domain=domain)
