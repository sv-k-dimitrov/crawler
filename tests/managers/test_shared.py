from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

from crawler.managers.shared import CrawlingDatabaseSetup, RequiredEnvironmentVariables


class TestCrawlingSetupValidations(TestCase):
    @patch("crawler.managers.shared.validate_environment_variables_from_Enum")
    def test_CrawlingSetup_raise_ValueError_for_missing_environment_variables(
        self, validations_call: MagicMock
    ) -> None:
        validations_call.side_effect = ValueError("this is mocked exception")

        self.assertRaises(ValueError, CrawlingDatabaseSetup)


class TestCrawlingSetupTablesCreation(TestCase):
    def setUp(self):
        return super().setUp()

    @skip("used for local testing only!")
    def test_CrawlingSetup_creates_all_tables(self) -> None:
        CrawlingDatabaseSetup()
