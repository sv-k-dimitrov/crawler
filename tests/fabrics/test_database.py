import os
from unittest import TestCase

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from crawler.managers.shared import CrawlingDatabaseSetup


class TestCrawlingDatabaseSetup(TestCase):
    def setUp(self) -> None:
        DB_NAME = os.getenv("DATABASE_NAME")
        self.database_name: str = os.getenv("DATABASE_NAME")
        DB_USER = os.getenv("DATABASE_USER")
        DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
        DB_HOST = os.getenv("DATABASE_HOST")
        DB_PORT = os.getenv("DATABASE_PORT")

        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

        self.cursor.execute(f"DROP DATABASE IF EXISTS test_db;")
        self.cursor.execute("CREATE DATABASE test_db;")

        os.environ["DATABASE_NAME"] = "test_db"

        self.db_setup = CrawlingDatabaseSetup()

        self.engine = self.db_setup.database_engine
        self.session = self.db_setup.session

        return super().setUp()

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.session.close()
        self.engine.dispose()
        os.environ["DATABASE_NAME"] = self.database_name
        self.cursor.execute(
            """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'test_db'
          AND pid <> pg_backend_pid();
        """
        )
        self.cursor.execute(f"DROP DATABASE IF EXISTS test_db;")
