from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from .config import get_settings


@contextmanager
def get_connection():
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_database() -> None:
    settings = get_settings()
    settings.upload_root.mkdir(parents=True, exist_ok=True)
    settings.output_root.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL,
                source_path TEXT NOT NULL,
                markdown_path TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS fragments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                fragment_index INTEGER NOT NULL,
                source_label TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT,
                text_content TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                section_index INTEGER NOT NULL,
                title TEXT NOT NULL,
                detailed_explanation TEXT NOT NULL,
                key_points_json TEXT NOT NULL,
                quiz_json TEXT NOT NULL,
                source_refs_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                scope TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source_refs_json TEXT NOT NULL,
                supplemental INTEGER NOT NULL DEFAULT 0,
                supplemental_notes TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
