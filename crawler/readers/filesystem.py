import json
import os
from typing import Any

from crawler.models.website import Website

from .exceptions import FileTypeNotSupportedError
from .interfaces import WebsiteModelReader


def dict_to_Website(content: dict[Any, Any]) -> Website:
    all_model_properties: set[str] = set(Website.__dataclass_fields__.keys())
    if "website" in all_model_properties:
        all_model_properties.remove("website")
        all_model_properties.add("target_url")

    if "label" in all_model_properties:
        all_model_properties.remove("label")
        all_model_properties.add("lookup_label")

    each_website_model_property: str
    for each_website_model_property in all_model_properties:
        if each_website_model_property not in content:
            raise ValueError(
                f"dict_to_Website - missing '{each_website_model_property}' property"
            )

    website_instance: Website = Website(
        website=content["target_url"], label=content["lookup_label"]
    )

    website_instance.count_pdf_pages = content["count_pdf_pages"]
    website_instance.count_html_pages = content["count_html_pages"]
    website_instance.largest_pdf_size = content["largest_pdf_size"]
    website_instance.largest_pdf_link = content["largest_pdf_link"]
    website_instance.pdf_scraped_pages = content["pdf_scraped_pages"]
    website_instance.html_scraped_pages = content["html_scraped_pages"]
    website_instance.scraped_pages = content["scraped_pages"]

    return website_instance


class FilesystemReader(WebsiteModelReader):
    def read(self, full_path_to_file: str) -> Website:
        if not os.path.isfile(full_path_to_file):
            raise IOError(
                f"{self.__class__.__name__} - provided input '{full_path_to_file}' it's not file!"
            )

        try:
            with open(full_path_to_file, "r") as file_desc:
                file_content: dict[Any, Any] = json.load(file_desc)

                if isinstance(file_content, list) and len(file_content) != 1:
                    raise ValueError(
                        f"{self.__class__.__name__} - invalid file content"
                    )

                if isinstance(file_content, list):
                    return dict_to_Website(file_content[0])

                if isinstance(file_content, dict):
                    return dict_to_Website(file_content)

        except (json.JSONDecodeError, IOError):
            raise FileTypeNotSupportedError(
                f"{self.__class__.__name__} - not supported file type"
            )
