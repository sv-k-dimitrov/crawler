import json
import os
from typing import Any
from unittest import TestCase
from uuid import uuid4

from crawler.models.website import Website
from crawler.stores.filesystem import FileSystemDataStore, FileType


class TestFileSystemDataStoreInit(TestCase):
    def test_FileSystemDataStore_raise_TypeError_for_invalid_input_type_parameter_file_name(
        self,
    ) -> None:
        try:
            FileSystemDataStore(
                file_name=1,
                directory_path="",
                format=FileType.JSON,
            )
        except TypeError as err:
            err_string: str = str(err)

            if err_string.startswith(
                f"{FileSystemDataStore.__name__}.__init__() missing"
            ):
                self.fail("not the valid TypeError needed")

    def test_FileSystemDataStore_raise_TypeError_for_invalid_input_type_parameter_directory_path(
        self,
    ) -> None:
        try:
            FileSystemDataStore(
                file_name="",
                directory_path=1,
                format=FileType.JSON,
            )
        except TypeError as err:
            err_string: str = str(err)

            if err_string.startswith(
                f"{FileSystemDataStore.__name__}.__init__() missing"
            ):
                self.fail("not the valid TypeError needed")

    def test_FileSystemDataStore_raise_TypeError_for_invalid_input_type_parameter_format(
        self,
    ) -> None:
        try:
            FileSystemDataStore(
                file_name="",
                directory_path="",
                format=1,
            )
        except TypeError as err:
            err_string: str = str(err)

            if err_string.startswith(
                f"{FileSystemDataStore.__name__}.__init__() missing"
            ):
                self.fail("not the valid TypeError needed")

    def test_FileSystemDataStore_raise_ValueError_for_invalid_input_type_parameter_file_name(
        self,
    ) -> None:
        self.assertRaises(
            ValueError,
            FileSystemDataStore,
            file_name="",
            directory_path="example",
            format=FileType.JSON,
        )

    def test_FileSystemDataStore_raise_ValueError_for_invalid_input_type_parameter_directory_path(
        self,
    ) -> None:
        self.assertRaises(
            ValueError,
            FileSystemDataStore,
            file_name="example",
            directory_path="",
            format=FileType.JSON,
        )

    def test_FileSystemDataStore_raise_IsADirectoryError_path_its_NOT_directory(
        self,
    ) -> None:
        full_file_path: str = os.path.join(os.getcwd(), "test.txt")

        with open(full_file_path, "w") as file:
            pass

        self.assertRaises(
            IsADirectoryError,
            FileSystemDataStore,
            file_name="example",
            directory_path=full_file_path,
            format=FileType.JSON,
        )

        os.remove(full_file_path)

    def test_FileSystemDataStore_raise_OSError_directory_was_NOT_found_on_filesystem(
        self,
    ) -> None:
        non_existing_directory: str = os.path.join(
            os.getcwd(), "non_existing_test_directory"
        )

        self.assertRaises(
            OSError,
            FileSystemDataStore,
            file_name="example",
            directory_path=non_existing_directory,
            format=FileType.JSON,
        )

    def test_FileSystemDataStore_raise_FileExistsError_final_file_already_exists(
        self,
    ) -> None:
        test_file_name: str = str(uuid4())
        test_directory: str = os.getcwd()
        test_file_type_ext: str = FileType.JSON.value

        full_path_to_test_file: str = os.path.join(
            test_directory, test_file_name + test_file_type_ext
        )

        with open(full_path_to_test_file, "w") as file:
            pass

        self.assertRaises(
            OSError,
            FileSystemDataStore,
            file_name=test_file_name,
            raise_error_if_file_exists=True,
            directory_path=test_directory,
            format=FileType.JSON,
        )

        os.remove(full_path_to_test_file)


class TestFileSystemDataStoreInternals(TestCase):
    def setUp(self) -> None:
        self.website_root_url: str = "http://example.com"
        self.website_label: str = "test_label"
        self.website_subpage_url: str = self.website_root_url + "/example"
        self.website_subpage_content: str = "example content"
        self.website_subpage_title: str = "example title"
        self.website_expected_safe_key: str = "http___example_com"

        self.website_test_instance: Website = Website(
            website=self.website_root_url, label=self.website_label
        )
        self.website_test_instance.add_html_page(
            page_url=self.website_subpage_url,
            page_content=self.website_subpage_content,
            page_title=self.website_subpage_title,
        )

        self.file_system_data_store_test_instance: FileSystemDataStore = (
            FileSystemDataStore(
                file_name=str(uuid4()), directory_path=os.getcwd(), format=FileType.JSON
            )
        )

        return super().setUp()

    def test_add_record_updates_internal_data_store(self) -> None:
        expected_amount_of_websites: int = 3

        i: int
        for i in range(expected_amount_of_websites):
            self.file_system_data_store_test_instance.add_record(
                self.website_test_instance
            )

        self.assertEqual(
            len(self.file_system_data_store_test_instance.data),
            expected_amount_of_websites,
        )

    def test_generate_content_returns_valid_dict_structure(self) -> None:
        expected_dict_structure: dict[str, Any] = {
            "target_url": self.website_root_url,
            "lookup_label": self.website_label,
            "safe_key": self.website_expected_safe_key,
            "count_pdf_pages": 0,
            "count_html_pages": 1,
            "largest_pdf_size": 0,
            "largest_pdf_link": "",
            "pdf_scraped_pages": {},
            "html_scraped_pages": {
                self.website_subpage_url: {
                    "title": self.website_subpage_title,
                    "content": self.website_subpage_content,
                }
            },
            "scraped_pages": {
                self.website_subpage_url: {
                    "title": self.website_subpage_title,
                    "content": self.website_subpage_content,
                }
            },
        }

        self.file_system_data_store_test_instance.add_record(self.website_test_instance)
        self.file_system_data_store_test_instance._generate_content()

        self.assertIsInstance(
            self.file_system_data_store_test_instance.data_content, list
        )
        self.assertIsInstance(
            self.file_system_data_store_test_instance.data_content[0], dict
        )
        expected_items: int = 1
        self.assertEqual(
            len(self.file_system_data_store_test_instance.data_content), expected_items
        )

        self.assertDictEqual(
            self.file_system_data_store_test_instance.data_content[0],
            expected_dict_structure,
        )

    def test_write_creates_file_with_valid_dictionary_structure(self) -> None:
        expected_dict_structure: dict[str, Any] = {
            "target_url": self.website_root_url,
            "lookup_label": self.website_label,
            "safe_key": self.website_expected_safe_key,
            "count_pdf_pages": 0,
            "count_html_pages": 1,
            "largest_pdf_size": 0,
            "largest_pdf_link": "",
            "pdf_scraped_pages": {},
            "html_scraped_pages": {
                self.website_subpage_url: {
                    "title": self.website_subpage_title,
                    "content": self.website_subpage_content,
                }
            },
            "scraped_pages": {
                self.website_subpage_url: {
                    "title": self.website_subpage_title,
                    "content": self.website_subpage_content,
                }
            },
        }

        self.file_system_data_store_test_instance.add_record(self.website_test_instance)
        self.file_system_data_store_test_instance.write()

        with open(
            self.file_system_data_store_test_instance.full_path_to_file, "r"
        ) as file:
            file_content: list[dict[str, Any]] = json.load(file)

        self.assertIsInstance(file_content, list)
        expected_amount_of_items: int = 1
        self.assertEqual(len(file_content), expected_amount_of_items)
        self.assertIsInstance(file_content[0], dict)
        self.assertDictEqual(file_content[0], expected_dict_structure)

        os.remove(self.file_system_data_store_test_instance.full_path_to_file)
