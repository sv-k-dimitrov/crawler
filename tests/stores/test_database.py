import os
from unittest import TestCase

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import inspect, text
from sqlalchemy.engine.result import ScalarResult

from crawler.managers.shared import CrawlingDatabaseSetup

DB_NAME = os.getenv("DATABASE_NAME")
DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")


class TestCrawlingDatabaseSetup(TestCase):
    def setUp(self) -> None:

        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

        self.drop_test_database()

        self.cursor.execute(f"CREATE DATABASE test_db;")

        os.environ["DATABASE_NAME"] = "test_db"

        self.db_setup = CrawlingDatabaseSetup()

        self.engine = self.db_setup.database_engine
        self.session = self.db_setup.session

    def drop_test_database(self):
        """Drops the testing database if it exists."""
        try:
            self.cursor.execute(
                """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'test_db'
            AND pid <> pg_backend_pid();
            """
            )
            self.cursor.execute(f"DROP DATABASE IF EXISTS test_db;")
        except Exception as e:
            print(f"Error while destroying the database: {e}")

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.session.close()
        self.engine.dispose()
        os.environ["DATABASE_NAME"] = DB_NAME
        self.drop_test_database()
        self.cursor.close()
        self.conn.close()

    def test_connection(self) -> None:
        try:
            with self.engine.connect() as connection:
                result: ScalarResult[int] = connection.execute(text("SELECT 1"))
                self.assertEqual(result.scalar(), 1)
        except Exception as e:
            self.fail(f"Database connection test failed: {e}")

    def test_table_creation(self) -> None:
        inspector = inspect(self.engine)
        tables: list[str] = inspector.get_table_names()

        expected_tables: list[str] = ["jobs", "pages", "targets"]
        for table in expected_tables:
            self.assertIn(table, tables)


class TestSqlDatabaseDataStoreWriteInterface(WebsiteFabric, TestCrawlingDatabaseSetup):

    def setUp(self) -> None:
        super().setUp()

        self.website_root_url = "http://example.com"
        self.website_label = "test_label"
        self.website_subpage_url = f"{self.website_root_url}/example"
        self.website_subpage_content = "example content"
        self.website_subpage_title = "example title"
        self.website_expected_safe_key = "http___example_com"

        self.website_test_instance = Website(
            website=self.website_root_url, label=self.website_label
        )
        self.website_test_instance.add_html_page(
            page_url=self.website_subpage_url,
            page_content=self.website_subpage_content,
            page_title=self.website_subpage_title,
        )
        self.website_test_instance.add_pdf_page(
            page_url=f"{self.website_root_url}/pdf",
            page_content="Pdf content",
            pdf_size=10,
            page_title="Pdf Title",
        )

        self.sql_system_data_store_test_instance = SqlDatabaseDataStore()

        self.crawl_website_instance = CrawlWebsite(
            website=self.website_root_url,
            website_label=self.website_label,
            crawl_depth=3,
            link_regex=r"^((ftp|http|https):\/\/)?(www.)?(?!.*(ftp|http|https|www.))[a-zA-Z0-9_-]+(\.[a-zA-Z]+)+((\/)[\w#]+)*(\/\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?\/?$",
            avoid_extensions=(".ttf",),
            stores=[self.sql_system_data_store_test_instance],
        )

    def test_write_creates_database_insert(self) -> None:
        self.sql_system_data_store_test_instance.add_record(self.website_test_instance)
        self.crawl_website_instance.run()

        with self.db_setup.session as session:
            result: int = session.query(Job).count()
            result_page: int = session.query(Page).count()
            result_target: int = session.query(Target).count()

        self.assertEqual(result_page, 3, "The Page record written to the database.")
        self.assertEqual(result_target, 2, "The Target record written to the database.")
        self.assertEqual(result, 1, "The Job record written to the database.")

    def test_insert_target_and_page(self) -> None:
        self.sql_system_data_store_test_instance.job_reference = Job(id=None)
        self.sql_system_data_store_test_instance.add_record(self.website_test_instance)
        self.sql_system_data_store_test_instance.write()

        with self.db_setup.session as session:
            result_page: int = session.query(Page).count()
            result_target: int = session.query(Target).count()

        self.assertEqual(result_page, 2, "The Page record written to the database.")
        self.assertEqual(result_target, 1, "The Target record written to the database.")

    def test_write_empty_data(self) -> None:
        website = Website(website=self.website_root_url, label="Empty Website")
        sql_data_store = SqlDatabaseDataStore()
        sql_data_store.job_reference = Job(id=None)
        sql_data_store.data = [website]

        sql_data_store.write()

        target_in_db: Target | None = (
            self.session.query(Target).filter_by(website=website.website).first()
        )
        self.assertIsNotNone(target_in_db)

        pages_in_db: list[Page] = (
            self.session.query(Page).filter_by(target_id=target_in_db.id).all()
        )
        self.assertEqual(len(pages_in_db), 0)

    def test_website_to_target_conversion(self) -> None:
        self.sql_system_data_store_test_instance.job_reference = Job(id=None)

        target: Target = self.sql_system_data_store_test_instance.website_to_target(
            self.website_test_instance
        )

        self.assertEqual(target.website, self.website_test_instance.website)
        self.assertEqual(
            target.crawling_job_id,
            self.sql_system_data_store_test_instance.job_reference.id,
        )
        self.assertEqual(
            target.count_pdf_pages, self.website_test_instance.count_pdf_pages
        )
        self.assertEqual(
            target.count_html_pages, self.website_test_instance.count_html_pages
        )
        self.assertEqual(
            target.website_metadata["label"], self.website_test_instance.label
        )

    def test_target_with_invalid_crawling_job(self) -> None:
        invalid_job_id: uuid.UUID = uuid.uuid4()
        target = Target(website=self.website_root_url, crawling_job_id=invalid_job_id)

        with self.assertRaises(Exception) as context:
            self.session.add(target)
            self.session.commit()

        self.assertIn("foreign key constraint", str(context.exception))

    def test_insert_pages(self) -> None:
        target = Target(
            website=self.website_root_url,
            crawling_job_id=None,
        )
        pdf_pages = {
            "http://example.com/pdf1": {"title": "PDF 1", "content": "Content 1"},
            "http://example.com/pdf2": {"title": "PDF 2", "content": "Content 2"},
        }
        html_pages = {
            "http://example.com/page1": {"title": "Page 1", "content": "Content 1"},
            "http://example.com/page2": {"title": "Page 2", "content": "Content 2"},
        }

        sql_data_store = SqlDatabaseDataStore()

        sql_data_store.insert_pages(target.id, pdf_pages, html_pages)

        pages_in_db = self.session.query(Page).filter_by(target_id=target.id).all()
        self.assertEqual(len(pages_in_db), 4)
        self.assertEqual(pages_in_db[0].website, "http://example.com/pdf1")
        self.assertEqual(pages_in_db[2].website, "http://example.com/page1")
