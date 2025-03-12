from unittest import TestCase

from crawler.models.website import Website


class TestWebsiteModelInit(TestCase):
    def test_Website_init_raise_TypeError_for_invalid_input_parameter_type(
        self,
    ) -> None:
        try:
            Website(website=1, label="test_label")
        except TypeError as err:
            err_string: str = str(err)

            if err_string.startswith(f"{Website.__name__}.__init__() missing"):
                self.fail("not the valid TypeError needed")


class TestWebsiteModelInternals(TestCase):
    def setUp(self) -> None:
        self.test_url: str = "https://www.almapharm.de"
        self.website_model_instance: Website = Website(
            website=self.test_url, label="test_label"
        )

        return super().setUp()

    def test_safe_key_creation_on_post_init(self) -> None:
        expected_safe_key: str = "https___www_almapharm_de"

        self.assertEqual(self.website_model_instance.safe_key, expected_safe_key)

    def test_add_page_raise_TypeError_for_invalid_input_parameter_type(self) -> None:
        self.assertRaises(
            TypeError,
            self.website_model_instance.add_html_page,
            page_url=1,
            page_content=1,
        )

    def test_add_page_inserts_properly_data_in_local_store_property(self) -> None:
        test_page_url: str = "test_page_url"
        test_page_content: str = "test_page_content"

        self.website_model_instance.add_html_page(
            page_url=test_page_url, page_content=test_page_content
        )

        self.assertDictEqual(
            {test_page_url: {"content": test_page_content, "title": "TITLE_UNDEFINED"}},
            self.website_model_instance.scraped_pages,
        )

    def test_Website_iterator(self) -> None:
        max_elements: int = 3

        i: int
        for i in range(max_elements):
            self.website_model_instance.add_html_page(
                page_url=f"test_page_url_{i}", page_content=f"test_page_content_{i}"
            )

        all_website_entries: list[dict[str, str]] = list()

        page_url: str
        page_content: str
        page_title: str
        for page_url, page_content, page_title in self.website_model_instance:
            all_website_entries.append({page_url: page_content})

        self.assertEqual(len(all_website_entries), max_elements)

    def test_Website_add_html_page_reflects_on_internal_counter(self) -> None:
        expected_count: int = 1

        self.website_model_instance.add_html_page("page_url", "page_content")

        self.assertEqual(self.website_model_instance.count_html_pages, expected_count)

    def test_Website_add_pdf_page_reflects_on_internal_counters(self) -> None:
        expected_count: int = 1
        example_pdf_url: str = "http://example.com/results.pdf"
        example_pdf_page_content: str = "example content"
        example_pdf_page_size: int = 200

        self.website_model_instance.add_pdf_page(
            example_pdf_url, example_pdf_page_content, example_pdf_page_size
        )

        self.assertEqual(self.website_model_instance.count_pdf_pages, expected_count)
        self.assertEqual(self.website_model_instance.largest_pdf_link, example_pdf_url)
        self.assertEqual(
            self.website_model_instance.largest_pdf_size, example_pdf_page_size
        )
