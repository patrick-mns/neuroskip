import os
from core.config import settings
from urllib.parse import urlparse
from peewee import SqliteDatabase, PostgresqlDatabase


if settings.connection_string_postgres:
    parsed = urlparse(settings.connection_string_postgres)
    db = PostgresqlDatabase(
    database=parsed.path[1:],
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port
    )
    print("Using postgres")
else:
    db = SqliteDatabase('segments.db')
    print("Using Sqlite")
    