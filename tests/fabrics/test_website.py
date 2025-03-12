import json
import os
from typing import Any
from unittest import TestCase

from crawler.models.website import Website


def load_file(file_path: str) -> list[dict[Any, Any]]:
    """Read's a file from OS, parse with JSON and returns standard Python dictionary

    Args:
        file_path (str): full path to file

    Returns:
        dict[Any, Any]: file content

    Raises:
        FileNotFoundError - file not found on file system
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"load_file - file '{file_path}' not found ")

    with open(file_path, "r") as file_descriptor:
        result: dict[Any, Any] = json.load(file_descriptor)

    return result


def load_data_to_Website_model(content: dict[Any, Any]) -> Website:
    """Transoform Python dicionary to Website model

    Args:
        content (dict[Any, Any]): website content

    Raises:
        ValueError: empty content

    Returns:
        Website: instance of the model
    """
    if not content:
        raise ValueError(f"load_data_to_Website_model - empty input")

    website_instance: Website = Website(
        website=content.get("target_url"), label=content.get("lookup_label")
    )
    website_instance.count_pdf_pages = content.get("count_pdf_pages")
    website_instance.count_html_pages = content.get("count_html_pages")
    website_instance.largest_pdf_size = content.get("largest_pdf_size")
    website_instance.largest_pdf_link = content.get("largest_pdf_link")
    website_instance.scraped_pages = content.get("scraped_pages")
    website_instance.pdf_scraped_pages = content.get("pdf_scraped_pages")
    website_instance.html_scraped_pages = content.get("html_scraped_pages")

    return website_instance


class WebsiteFabric(TestCase):
    def setUp(self):
        folder_all_tests: str = "tests"
        folder_all_examples: str = "examples"

        self.full_path_empty_website_content: str = os.path.join(
            os.getcwd(), folder_all_tests, folder_all_examples, "website-empty.json"
        )
        self.full_path_website_with_full_content: str = os.path.join(
            os.getcwd(),
            folder_all_tests,
            folder_all_examples,
            "website-full-content.json",
        )

        self.website_empty: Website = load_data_to_Website_model(
            load_file(self.full_path_empty_website_content)[0]
        )
        self.website_full_content: Website = load_data_to_Website_model(
            load_file(self.full_path_website_with_full_content)[0]
        )

        return super().setUp()
