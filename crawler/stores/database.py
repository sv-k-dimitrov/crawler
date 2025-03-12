import logging
from dataclasses import dataclass, field
from typing import Dict

from crawler.managers.shared import CrawlingDatabaseSetup
from crawler.models.database.page import Page, PageContentTypes, PageTypes
from crawler.models.database.target import Target
from crawler.models.utils import (
    TextStatistics,
    calculate_text_statistics,
    detect_page_content_type,
)
from crawler.models.website import ContentDefaults, Website

from .generic import _StoreDataRecords
from .interfaces import WebsiteDataStoreRecordWriteInterface

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class SqlDatabaseDataStore(
    CrawlingDatabaseSetup,
    _StoreDataRecords,
    WebsiteDataStoreRecordWriteInterface,
):
    target_instance: Target = field(init=False)

    def insert_page(
        self,
        page_url: str,
        page_content: Dict[str, str],
        page_type: PageTypes,
    ):
        has_title = (
            True
            if page_content.get("title") != ContentDefaults.TITLE_UNDEFINED.value
            else False
        )
        has_content = (
            True
            if page_content.get("content") != ContentDefaults.CONTENT_UNDEFINED.value
            else False
        )

        page_content_type: PageContentTypes = PageContentTypes.UNKNOWN
        try:
            page_content_type: PageContentTypes = detect_page_content_type(
                page_content["content"]
            )
        except Exception as err:
            logger.error(
                f"{self.__class__.__name__} - unhandled exception in detect_page_content_type. Error details: {err}"
            )

        text_stats: TextStatistics = TextStatistics()

        if (
            page_content_type == PageContentTypes.TEXT
            or page_content_type == PageContentTypes.TEXT_unicode
        ):
            text_stats = calculate_text_statistics(page_content.get("content"))

        page_instance: Page = Page(
            target_id=self.target_instance.id,
            page_type=page_type.value,
            page_content_type=page_content_type.value,
            website=page_url,
            has_title=has_title,
            has_content=has_content,
            min_word_length=text_stats.min_word_length,
            mean_word_length=text_stats.mean_word_length,
            max_word_length=text_stats.max_word_length,
            min_sentence_length=text_stats.min_sentence_length,
            mean_sentence_length=text_stats.mean_sentence_length,
            max_sentence_length=text_stats.max_sentence_length,
        )

        self.session.add(page_instance)
        self.session.commit()

    def write(self):
        website: Website
        for website in self.data:
            page_url: str
            page_content: Dict[str, str]
            for page_url, page_content in website.pdf_scraped_pages.items():
                page_type: PageTypes = PageTypes.PDF

                self.insert_page(page_url, page_content, page_type)

            for page_url, page_content in website.html_scraped_pages.items():
                page_type: PageTypes = PageTypes.HTML

                self.insert_page(page_url, page_content, page_type)

        self.write_success = True
