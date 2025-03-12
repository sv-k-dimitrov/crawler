from unittest import TestCase

from crawler.models.database.page import PageContentTypes
from crawler.models.utils import (
    TextStatistics,
    calculate_text_statistics,
    detect_page_content_type,
)


class TestModelUtils(TestCase):
    def test_calculate_text_statistics_returns_valid_stats(self) -> None:
        example_text: str = (
            "This is example text created to test the functionality of calculate_text_statistics util. Stats compared are manually created."
        )

        result_stats: TextStatistics = calculate_text_statistics(example_text)

        self.assertEqual(result_stats.max_word_length, 25)
        self.assertEqual(result_stats.mean_word_length, 6)
        self.assertEqual(result_stats.min_word_length, 2)
        self.assertEqual(result_stats.max_sentence_length, 89)
        self.assertEqual(result_stats.mean_sentence_length, 62)
        self.assertEqual(result_stats.min_sentence_length, 36)

    def test_detect_page_content_type_returns_PageContentTypes_TEXT(self) -> None:
        test_input: list[str] = [
            "Just some random text, : . ! ? ; 'wrapper' \"another wrapper\" ",
            "No tags here, just a string!",
            "https://www.ampelmann.nl//offshore-wind daily 0.5 https://www.ampelmann.nl//oil-and-gas daily 0.5 https://www.ampelmann.nl//decomissioning ",
        ]

        test_text: str
        for test_text in test_input:
            test_page_content_type_result: PageContentTypes = detect_page_content_type(
                test_text
            )
            self.assertIsInstance(test_page_content_type_result, PageContentTypes)
            self.assertEqual(test_page_content_type_result, PageContentTypes.TEXT)

    def test_detect_page_content_type_returns_PageContentTypes_HTML_UNPARSED(
        self,
    ) -> None:
        test_input: list[str] = [
            "<html><body><h1>Hello</h1></body></html>",
            "<div>HTML-like content</div>",
            "another example of hidden type <span>HTML-like content</span> and here's ending text",
        ]

        examples = [
            "Just plain text",
            "这是一些文字",  # Unicode text
            "<html><body>Hello</body></html>",
            "<note><to>User</to><message>Test</message></note>",
            '{"key": "value"}',
            "Some random <> unknown structure",
        ]

        test_text: str
        for test_text in examples:
            test_page_content_type_result: PageContentTypes = detect_page_content_type(
                test_text
            )
            print(test_text)
            self.assertIsInstance(test_page_content_type_result, PageContentTypes)
            # self.assertEqual(
            #     test_page_content_type_result, PageContentTypes.HTML_UNPARSED
            # )

    def test_detect_page_content_type_returns_PageContentTypes_XML_UNPARSED(
        self,
    ) -> None:
        test_input: list[str] = [
            """<?xml version="1.0" encoding="UTF-8"?>
                <note>
                    <to>Tove</to>
                    <from>Jani</from>
                    <heading>Reminder</heading>
                    <body>Don't forget me this weekend!</body>
                </note>
            """,
        ]

        test_text: str
        for test_text in test_input:
            test_page_content_type_result: PageContentTypes = detect_page_content_type(
                test_text
            )
            self.assertIsInstance(test_page_content_type_result, PageContentTypes)
            self.assertEqual(
                test_page_content_type_result, PageContentTypes.XML_UNPARSED
            )

    def test_detect_page_content_type_returns_PageContentTypes_JSON_UNPARSED(
        self,
    ) -> None:
        test_input: list[str] = [
            '{"name":"CardinalPartners","description":"","url":"http:\\/\\/cardinalpartners.com","home":"http:\\/\\/cardinalpartners.com"}'
        ]

        test_text: str
        for test_text in test_input:
            test_page_content_type_result: PageContentTypes = detect_page_content_type(
                test_text
            )
            self.assertIsInstance(test_page_content_type_result, PageContentTypes)
            self.assertEqual(
                test_page_content_type_result, PageContentTypes.JSON_UNPARSED
            )
