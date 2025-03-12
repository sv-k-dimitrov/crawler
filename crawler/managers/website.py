import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union
from uuid import UUID

import requests
from aiohttp import ClientResponse
from bs4 import BeautifulSoup, NavigableString, Tag
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchain_core.documents import Document
from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from requests import Response

from crawler.models.database import Job, Target
from crawler.models.shared import WebsiteModelTransformations
from crawler.models.website import Website
from crawler.stores.aws import AwsDataStore
from crawler.stores.database import SqlDatabaseDataStore
from crawler.stores.filesystem import FileSystemDataStore
from crawler.stores.interfaces import (
    WebsiteDataStoreKeepAndWriteInterface,
    WebsiteDataStoreRecordKeepInterface,
    WebsiteDataStoreRecordWriteInterface,
)

from .shared import CrawlingDatabaseSetup, CrawlingDatabaseSetupValidations

logger: logging.Logger = logging.getLogger(__name__)


def html_extractor(html: str) -> str:
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

    logger.debug(f"html_extractor - for HTML {html}, using BeautifulSoup: {soup}")

    title: Tag | None = soup.title
    title_filters: list[str] = ["nicht gefunden", "not found", "error"]

    if title:
        title = title.string
        if isinstance(title, str):
            for filter in title_filters:
                if filter in title.lower():
                    logger.info(
                        f"html_extractor - title '{title.lower()}' match found for filter '{filter}'. Returning empty string as result."
                    )

                    return ""
    else:
        title = "No title"

    text: str = " ".join(soup.text.split())

    logging.debug(f"html_extractor - text response: {text}")
    return text


def metadata_extractor(
    raw_html: str, url: str, response: Union[Response, ClientResponse]
) -> dict[Any, Any]:
    content_type = getattr(response, "headers").get("Content-Type", "")
    metadata = {"source": url, "content_type": content_type}

    soup = BeautifulSoup(raw_html, "html.parser")

    if title := soup.find("title"):
        metadata["title"] = title.get_text()

    description: Tag | NavigableString | None = soup.find(
        "meta", attrs={"name": "description"}
    )
    if description:
        metadata["description"] = description.get("content")

    if html := soup.find("html"):
        metadata["language"] = html.get("lang", None)

    return metadata


class DataStoreTypes(Enum):
    SQL: object = SqlDatabaseDataStore
    FILESYSTEM: object = FileSystemDataStore
    AWS: object = AwsDataStore


def get_store_by_type(
    stores: WebsiteDataStoreKeepAndWriteInterface,
    lookup_data_store_type: DataStoreTypes,
) -> WebsiteDataStoreKeepAndWriteInterface | None:
    store: WebsiteDataStoreKeepAndWriteInterface
    for store in stores:
        if isinstance(store, lookup_data_store_type.value):
            return store

    return None


@dataclass
class CrawlWebsite(CrawlingDatabaseSetup):
    """Crawl orchestrator/ fabric which performs recursive scrape
    starting with a root URL and performs recursive scrape of nested URLs based on the requested depth.

    Allows filtering URLs based on regex and blocking scrapes for URLs containing specific extensions.

    Allows granular write to multiple data stores, based on the need.

    NOTE: Current implementation is scroped around crawling a single website and all operations are performed synchronously.

    Raises:
        TypeError: invalid input type for any of the input parameters
        ValueError: invalid/ empty value for any of the input parameters
    """

    website: str
    website_label: str
    crawl_depth: int
    link_regex: str
    avoid_extensions: tuple[str]
    stores: list[WebsiteDataStoreKeepAndWriteInterface]
    mark_job_completion: bool = field(default=True)

    website_instance: Website = field(init=False)
    job_instance: Job = field(init=False, default=None)
    target_instance: Target = field(init=False, default=None)
    job_instance_uuid: UUID = field(default=None)
    http_timeout: int = field(default=30)
    headers: dict[str, Any] = field(init=False, default_factory=dict)

    sql_store_found: bool = field(init=False, default=False)
    filesystem_store_found: bool = field(init=False, default=False)
    aws_store_found: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if not isinstance(self.crawl_depth, int):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter. Got '{type(self.crawl_depth)}', expceted: int"
            )

        if not isinstance(self.link_regex, str):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter. Got '{type(self.link_regex)}', expceted: string"
            )

        if not isinstance(self.avoid_extensions, tuple):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter. Got '{type(self.avoid_extensions)}', expceted: tuple[str]"
            )

        if not isinstance(self.stores, list):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter. Got '{type(self.stores)}', expceted: list[WebsiteDataStoreRecordWriteInterface]"
            )

        self.sql_store_found: bool = False
        self.filesystem_store_found: FileSystemDataStore = False

        sql_store_reference: SqlDatabaseDataStore = None

        store: WebsiteDataStoreKeepAndWriteInterface
        for store in self.stores:
            if not isinstance(
                store,
                WebsiteDataStoreRecordKeepInterface,
            ) or not isinstance(
                store,
                WebsiteDataStoreRecordWriteInterface,
            ):
                raise TypeError(
                    f"{self.__class__.__name__} - provided store {store.__class__.__name__} doesn't have {WebsiteDataStoreKeepAndWriteInterface.__name__}"
                )

            if isinstance(store, CrawlingDatabaseSetupValidations):
                super().__post_init__()
                self.sql_store_found = True
                sql_store_reference = store

            if isinstance(store, FileSystemDataStore):
                self.filesystem_store_found = True

            if isinstance(store, AwsDataStore):
                self.aws_store_found = True

        if not self.website or not self.link_regex:
            raise ValueError(
                f"{self.__class__.__name__} - invalid value for string parameter"
            )

        self.website_instance = Website(website=self.website, label=self.website_label)

        software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

        user_agent_rotator = UserAgent(
            software_names=software_names, operating_systems=operating_systems
        )

        random_user_agent = user_agent_rotator.get_random_user_agent()

        self.headers = {"User-Agent": random_user_agent}

        logger.info(f"{self.__class__.__name__} - user agent user: {random_user_agent}")

        if self.sql_store_found and self.job_instance_uuid:
            self.job_instance: Job = (
                self.session.query(Job).filter_by(id=self.job_instance_uuid).first()
            )

            if not self.job_instance:
                raise ValueError(
                    f"{self.__class__.__name__} - job ID '{self.job_instance_uuid}' was used as reference, but none was found in the database"
                )

        if self.sql_store_found and not self.job_instance:
            self.job_instance = Job(
                depth=self.crawl_depth,
            )
            self.session.add(self.job_instance)
            self.session.commit()

        if self.sql_store_found and self.job_instance:
            self.target_instance: Target = (
                WebsiteModelTransformations.website_model_to_Target_SQL_model(
                    website=self.website_instance, job=self.job_instance
                )
            )
            self.session.add(self.target_instance)
            self.session.commit()

        if self.sql_store_found:
            sql_store_reference.target_instance = self.target_instance

    def _add_record_for_pdf_page(self, document: Document) -> None:
        document_url: str = document.metadata["source"]

        pdf_response: requests.Response = requests.head(document_url)

        file_size: int = 0
        if "Content-Length" in pdf_response.headers:
            file_size = int(pdf_response.headers["Content-Length"])

        pdf_pages: list[Document] = PyMuPDFLoader(file_path=document_url).load()

        content_all_pages: list[str] = list()
        temp_doc: Document
        for temp_doc in pdf_pages:
            content_all_pages.append(temp_doc.page_content)

        document_content: str = " ".join(content_all_pages)

        self.website_instance.add_pdf_page(
            page_url=document_url, page_content=document_content, pdf_size=file_size
        )

    def _add_record_for_html_page(self, document: Document) -> None:
        document_url: str = document.metadata["source"]
        document_content: str = document.page_content
        document_title: str = (
            document.metadata["title"] if "title" in document.metadata else ""
        )

        avoid_document_insert: bool = False

        avoided_extension: str
        for avoided_extension in self.avoid_extensions:
            if avoided_extension in document_url:
                logger.warning(
                    f"{self.__class__.__name__} - found match with extension requested to be avoided for store in the database, URL '{document_url}' matched with extension '{avoided_extension}'!"
                )

                avoid_document_insert = True
                break

        if not avoid_document_insert:
            self.website_instance.add_html_page(
                page_url=document_url,
                page_content=document_content,
                page_title=document_title,
            )

    def _run_crawling(self) -> None:
        logger.info(
            f"{self.__class__.__name__} - starting crawling for website: {self.website}"
        )

        loader = RecursiveUrlLoader(
            url=self.website,
            max_depth=self.crawl_depth,
            headers=self.headers,
            extractor=html_extractor,
            metadata_extractor=metadata_extractor,
            check_response_status=True,
            link_regex=self.link_regex,
            timeout=self.http_timeout,
        )

        loaded_docs: list[Document] = loader.load()

        if not self.avoid_extensions:
            logger.warning(
                f"{self.__class__.__name__} - the filter for bad extensions to be avoided is empty!"
            )

        document: Document
        for document in loaded_docs:
            if (
                ".pdf" in document.metadata["source"]
                or document.metadata["content_type"] == "application/pdf"
            ):
                self._add_record_for_pdf_page(document)

                continue

            self._add_record_for_html_page(document)

        logger.info(
            f"{self.__class__.__name__} - completed crawling for website: {self.website}"
        )

    def _update_target_model_with_website_model_data(self) -> None:
        if self.sql_store_found:
            self.target_instance.count_pdf_pages = self.website_instance.count_pdf_pages
            self.target_instance.count_html_pages = (
                self.website_instance.count_html_pages
            )
            self.target_instance.largest_pdf_link = (
                self.website_instance.largest_pdf_link
            )
            self.target_instance.largest_pdf_size = (
                self.website_instance.largest_pdf_size
            )

            self.session.add(self.target_instance)
            self.session.commit()

    def run(self) -> None:
        self._run_crawling()

        if self.sql_store_found:
            self.target_instance.set_finished(self.session)

        self._update_target_model_with_website_model_data()

        store: WebsiteDataStoreKeepAndWriteInterface
        for store in self.stores:
            store.add_record(self.website_instance)

        aws_store: AwsDataStore = get_store_by_type(self.stores, DataStoreTypes.AWS)
        if aws_store:
            aws_store.filename = self.target_instance.id

        store: WebsiteDataStoreKeepAndWriteInterface
        for store in self.stores:
            try:
                store.write()
            except Exception as err:
                logger.error(
                    f"{self.__class__.__name__} - store {store.__class__.__name__} failed on write operation. Error details: {err}"
                )

        if self.sql_store_found and aws_store and aws_store.write_success:
            self.target_instance.s3_bucket = aws_store.s3_bucket_name
            self.target_instance.s3_location = aws_store.filename

        filesystem_store: FileSystemDataStore = get_store_by_type(
            self.stores, DataStoreTypes.FILESYSTEM
        )
        if self.sql_store_found and filesystem_store and filesystem_store.write_success:
            self.target_instance.filesystem_location = (
                filesystem_store.full_path_to_file
            )

        if self.sql_store_found:
            self.session.add(self.target_instance)
            self.session.commit()

        if self.sql_store_found and self.mark_job_completion:
            self.job_instance.set_finished(self.session)

        logger.info(
            f"{self.__class__.__name__} - closing operation for: {self.website_instance}"
        )
