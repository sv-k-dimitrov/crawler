import os
from typing import Any
from unittest import TestCase

from crawler.models.website import Website
from crawler.readers.exceptions import FileTypeNotSupportedError
from crawler.readers.filesystem import FilesystemReader, dict_to_Website
from tests.fabrics.test_examples import ExamplesTest


class TestTransformDictToWebsiteInstance(TestCase):
    def setUp(self):
        self.test_valid_website_content: dict[Any, Any] = {
            "target_url": "https://abris-capital.com",
            "lookup_label": "Abris CEE Mid-Market Fund III",
            "safe_key": "https___abris_capital_com",
            "count_pdf_pages": 6,
            "count_html_pages": 78,
            "largest_pdf_size": 16953418,
            "largest_pdf_link": "https://abris-capital.com/wp-content/uploads/2022/06/ABRIS-ESG-Report-2021.pdf",
            "pdf_scraped_pages": {},
            "html_scraped_pages": {},
            "scraped_pages": {},
        }
        self.test_invalid_website_content: dict[Any, Any] = {
            "target_url": "https://abris-capital.com",
            "lookup_label": "Abris CEE Mid-Market Fund III",
            "safe_key": "https___abris_capital_com",
            "count_pdf_pages": 6,
            "count_html_pages": 78,
            "largest_pdf_size": 16953418,
            "largest_pdf_link": "https://abris-capital.com/wp-content/uploads/2022/06/ABRIS-ESG-Report-2021.pdf",
        }

        return super().setUp()

    def test_raise_ValueError_for_invalid_content(self) -> None:
        self.assertRaises(
            ValueError, dict_to_Website, self.test_invalid_website_content
        )

    def test_returns_valid_Website_instance(self) -> None:
        website: Website = dict_to_Website(self.test_valid_website_content)

        self.assertIsInstance(website, Website)


class TestFilesystemReaderInternals(ExamplesTest):
    def setUp(self):
        super().setUp()

        self.test_filesystem_reader_instance: FilesystemReader = FilesystemReader()
        self.path_to_not_supported_file: str = os.path.join(
            self.full_path_to_example_folder,
            "website_model_not_supported_file_type.yaml",
        )
        self.path_to_supported_file: str = os.path.join(
            self.full_path_to_example_folder,
            "website-full-content.json",
        )

    def test_read_raise_IOError(self) -> None:
        self.assertRaises(
            IOError,
            self.test_filesystem_reader_instance.read,
            "non_existing_path",
        )

    def test_read_raise_FileTypeNotSupportedError(self) -> None:
        self.assertRaises(
            FileTypeNotSupportedError,
            self.test_filesystem_reader_instance.read,
            self.path_to_not_supported_file,
        )

    def test_read_return_Website_model_instance(self) -> None:
        result: Website = self.test_filesystem_reader_instance.read(
            self.path_to_supported_file
        )

        self.assertIsInstance(result, Website)
