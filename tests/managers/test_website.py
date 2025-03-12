import re
from dataclasses import dataclass
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch
from uuid import UUID

from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_core.documents import Document
from langchain_core.utils.html import PREFIXES_TO_IGNORE_REGEX, SUFFIXES_TO_IGNORE
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from sqlalchemy import Engine

from crawler.managers.shared import CrawlingDatabaseSetupValidations, create_job
from crawler.managers.website import (
    CrawlWebsite,
    DataStoreTypes,
    get_store_by_type,
    html_extractor,
    metadata_extractor,
)
from crawler.models.database import Job
from crawler.models.website import Website
from crawler.stores.aws import AwsDataStore
from crawler.stores.database import SqlDatabaseDataStore
from crawler.stores.filesystem import FileSystemDataStore, FileType
from crawler.stores.interfaces import (
    WebsiteDataStoreKeepAndWriteInterface,
    WebsiteDataStoreRecordKeepInterface,
    WebsiteDataStoreRecordWriteInterface,
)
from tests.fabrics.test_database import TestCrawlingDatabaseSetup

bad_ext_tpl = (
    *SUFFIXES_TO_IGNORE,
    (".mp4"),
    (".woff"),
    (".woff2"),
    (".webmanifest"),
    (".ttf"),
)

bad_ext_tpl_pdf = (
    *SUFFIXES_TO_IGNORE,
    (".pdf"),
    (".mp4"),
    (".woff"),
    (".woff2"),
    (".webmanifest"),
    (".ttf"),
)

SUFFIXES_TO_IGNORE_REGEX = (
    "(?!" + "|".join([re.escape(s) + r"[\#'\"]" for s in bad_ext_tpl]) + ")"
)

PROFILER_LINK_REGEX = (
    rf"href=[\"']{PREFIXES_TO_IGNORE_REGEX}((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)[\#'\"]"
)


@dataclass
class MockStoreWithKeepOnlyInterfaceOnly(WebsiteDataStoreRecordKeepInterface):
    def add_record(self, website):
        pass


@dataclass
class MockStoreWithWriteOnlyInterface(WebsiteDataStoreRecordWriteInterface):
    def write(self):
        pass


@dataclass
class MockStoreWithBothKeepAndWriteInterfaces(
    WebsiteDataStoreRecordKeepInterface, WebsiteDataStoreRecordWriteInterface
):
    def add_record(self, website):
        pass

    def write(self):
        pass


@dataclass
class MockSqlDataStore(
    CrawlingDatabaseSetupValidations,
    WebsiteDataStoreRecordKeepInterface,
    WebsiteDataStoreRecordWriteInterface,
):
    def add_record(self, website):
        pass

    def write(self):
        pass


class TestCrawlWebsiteValidations(TestCase):
    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_crawl_depth(
        self,
    ) -> None:
        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth="3",
            link_regex="test_regex",
            avoid_extensions=("test", "another_test"),
            stores=["test"],
        )

    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_link_regex(
        self,
    ) -> None:
        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex=3,
            avoid_extensions=("test", "another_test"),
            stores=["test"],
        )

    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_avoid_extensions(
        self,
    ) -> None:
        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex="3",
            avoid_extensions=["test"],
            stores=["test"],
        )

    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_stores(
        self,
    ) -> None:
        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex=3,
            avoid_extensions=("test", "another_test"),
            stores=("test"),
        )

    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_stores_which_include_WebsiteDataStoreRecordKeepInterface_only(
        self,
    ) -> None:
        test_store = MockStoreWithKeepOnlyInterfaceOnly()

        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex="3",
            avoid_extensions=("test", "another_test"),
            stores=[test_store],
        )

    def test_CrawlWebsite_raise_TypeError_for_invalid_input_type_for_stores_which_include_WebsiteDataStoreRecordWriteInterface_only(
        self,
    ) -> None:
        test_store = MockStoreWithWriteOnlyInterface()

        self.assertRaises(
            TypeError,
            CrawlWebsite,
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex="3",
            avoid_extensions=("test", "another_test"),
            stores=[test_store],
        )

    def test_CrawlWebsite_does_NOT_raise_exception_creates_SQL_engine(self) -> None:
        test_store = MockSqlDataStore()

        test_crawl_instance: CrawlWebsite = CrawlWebsite(
            website="test_website",
            website_label="test_label",
            crawl_depth=3,
            link_regex="3",
            avoid_extensions=("test", "another_test"),
            stores=[test_store],
        )

        self.assertIsInstance(test_crawl_instance.database_engine, Engine)
        self.assertIsInstance(test_crawl_instance.website_instance, Website)


class TestCrawlWebsiteJobParameterInput(TestCrawlingDatabaseSetup):
    def test_job_create_with_CrawlWebsite_fabctic_setup(self) -> None:
        test_depth: int = 10
        result: UUID = create_job(test_depth)
        mock_sql_store: MockSqlDataStore = MockSqlDataStore()

        crawling_fabric_instance: CrawlWebsite = CrawlWebsite(
            website="test_website",
            website_label="test_website_label",
            crawl_depth=3,
            link_regex=r"^((ftp|http|https):\/\/)?(www.)?(?!.*(ftp|http|https|www.))[a-zA-Z0-9_-]+(\.[a-zA-Z]+)+((\/)[\w#]+)*(\/\w+\?[a-zA-Z0-9_]+=\w+(&[a-zA-Z0-9_]+=\w+)*)?\/?$",
            avoid_extensions=(".ttf",),
            stores=[mock_sql_store],
            job_instance_uuid=result,
        )

        self.assertEqual(crawling_fabric_instance.job_instance.id, result)


class TestRecursiveUrlLoader(TestCase):
    def setUp(self):
        self.crawl_depth: int = 3
        self.website: str = "https://fireboard.net/"
        self.link_regex: str = PROFILER_LINK_REGEX

        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

        user_agent_rotator = UserAgent(
            software_names=software_names, operating_systems=operating_systems
        )

        random_user_agent = user_agent_rotator.get_random_user_agent()

        self.headers = {"User-Agent": random_user_agent}

        return super().setUp()

    @skip("test for local troubleshooting only!")
    def test_user_agent_modify(self) -> None:
        print()

        loader = RecursiveUrlLoader(
            url=self.website,
            max_depth=self.crawl_depth,
            headers=self.headers,
            extractor=html_extractor,
            metadata_extractor=metadata_extractor,
            check_response_status=True,
            link_regex=self.link_regex,
            timeout=20,
        )

        loaded_docs: list[Document] = loader.load()

        print()


class TestHelpers(TestCase):
    @patch.object(FileSystemDataStore, "__post_init__", return_value=None)
    @patch.object(AwsDataStore, "__post_init__", return_value=None)
    @patch.object(SqlDatabaseDataStore, "__post_init__", return_value=None)
    def setUp(
        self,
        mock_sql_data_store: MagicMock,
        mock_aws_data_store: MagicMock,
        mock_filesystem_store: MagicMock,
    ):
        print()

        self.filesystem_store_instnace: FileSystemDataStore = FileSystemDataStore(
            file_name="exmaple",
            directory_path="example",
            format=FileType.JSON,
        )
        self.aws_store_instance: AwsDataStore = AwsDataStore(s3_bucket_name="example")
        self.sql_store_instance: SqlDatabaseDataStore = SqlDatabaseDataStore()

        return super().setUp()

    def test_get_store_by_type_returns_None_for_missing_store_reference(self) -> None:
        test_list_stores: list[WebsiteDataStoreKeepAndWriteInterface] = [
            self.filesystem_store_instnace,
            self.sql_store_instance,
        ]

        lookup_result: None = get_store_by_type(test_list_stores, DataStoreTypes.AWS)

        self.assertIsNone(lookup_result)

    def test_get_store_by_type_returns_store_reference_after_lookup(self) -> None:
        test_list_stores: list[WebsiteDataStoreKeepAndWriteInterface] = [
            self.filesystem_store_instnace,
            self.aws_store_instance,
            self.sql_store_instance,
        ]

        lookup_result: AwsDataStore = get_store_by_type(
            test_list_stores, DataStoreTypes.AWS
        )

        self.assertIsInstance(lookup_result, AwsDataStore)
