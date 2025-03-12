import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator


class ContentDefaults(Enum):
    TITLE_UNDEFINED: str = "TITLE_UNDEFINED"
    CONTENT_UNDEFINED: str = "CONTENT_UNDEFINED"


def is_empty_or_whitespace(s: str) -> bool:
    return not s.strip()


@dataclass
class Website:
    website: str
    label: str

    safe_key: str = field(init=False)
    count_pdf_pages: int = field(init=False, default=0)
    count_html_pages: int = field(init=False, default=0)
    largest_pdf_size: int = field(init=False, default=0)
    largest_pdf_link: str = field(init=False, default="")
    scraped_pages: dict[str, dict[str, str]] = field(init=False, default_factory=dict)
    pdf_scraped_pages: dict[str, dict[str, str]] = field(
        init=False, default_factory=dict
    )
    html_scraped_pages: dict[str, dict[str, str]] = field(
        init=False, default_factory=dict
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} - root URL: {self.website}, label: {self.label}, safe_key: {self.safe_key}, PDF pages count: {self.count_pdf_pages}, HTML pages count: {self.count_html_pages}"

    def __post_init__(self) -> None:
        if not isinstance(self.website, str):
            raise TypeError(
                f"{self.__class__.__name__} - input parameter doesn't match requried type. Got '{type(self.website)}', expects: string"
            )

        self.safe_key: str = re.sub(
            r"[^a-z0-9]", "_", self.website, flags=re.IGNORECASE
        ).lower()

    def add_html_page(
        self, page_url: str, page_content: str, page_title: str = ""
    ) -> None:
        if (
            not isinstance(page_url, str)
            or not isinstance(page_content, str)
            or not isinstance(page_title, str)
        ):
            raise TypeError(
                f"{self.__class__.__name__} - input parameter doesn't match requried type!"
            )

        if not page_content or is_empty_or_whitespace(page_content):
            page_content = ContentDefaults.CONTENT_UNDEFINED.value

        if not page_title or is_empty_or_whitespace(page_content):
            page_title = ContentDefaults.TITLE_UNDEFINED.value

        page_data: Dict[str, str] = {"title": page_title, "content": page_content}
        self.scraped_pages[page_url] = page_data
        self.html_scraped_pages[page_url] = page_data
        self.count_html_pages += 1

    def add_pdf_page(
        self, page_url: str, page_content: str, pdf_size: int, page_title: str = ""
    ) -> None:
        if (
            not isinstance(page_url, str)
            or not isinstance(page_content, str)
            or not isinstance(page_title, str)
            or not isinstance(pdf_size, int)
        ):
            raise TypeError(
                f"{self.__class__.__name__} - input parameter doesn't match requried type!"
            )

        if not page_content or is_empty_or_whitespace(page_content):
            page_content = ContentDefaults.CONTENT_UNDEFINED.value

        if not page_title or is_empty_or_whitespace(page_content):
            page_title = ContentDefaults.TITLE_UNDEFINED.value

        page_data: Dict[str, str] = {"title": page_title, "content": page_content}
        self.scraped_pages[page_url] = page_data
        self.pdf_scraped_pages[page_url] = page_data
        self.count_pdf_pages += 1

        if pdf_size > self.largest_pdf_size:
            self.largest_pdf_size = pdf_size
            self.largest_pdf_link = page_url

    def __iter__(self) -> Iterator[tuple[str, str, str]]:
        for key, value in self.scraped_pages.items():
            yield key, value["content"], value["title"]

    def to_json(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()

        result["target_url"] = self.website
        result["lookup_label"] = self.label if self.label else "missing_label"
        result["safe_key"] = self.safe_key
        result["count_pdf_pages"] = self.count_pdf_pages
        result["count_html_pages"] = self.count_html_pages
        result["largest_pdf_size"] = self.largest_pdf_size
        result["largest_pdf_link"] = self.largest_pdf_link

        result["pdf_scraped_pages"] = self.pdf_scraped_pages
        result["html_scraped_pages"] = self.html_scraped_pages
        result["scraped_pages"] = self.scraped_pages

        return result
