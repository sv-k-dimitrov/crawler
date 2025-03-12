import os
from enum import Enum
from unittest import TestCase

from crawler.managers.utils import validate_environment_variables_from_Enum


class MockRequiredEnvVars(str, Enum):
    TEST_ONE: str = "TEST_ONE"
    TEST_TWO: str = "test_two"


class MockRequiredEnvVarsValues(str, Enum):
    TEST_ONE: str = "test_input_one"
    TEST_TWO: str = "Test_Input_Two"


class TestManagerUtils(TestCase):
    def test_validate_environment_variables_from_Enum_raise_TypeError(self) -> None:
        self.assertRaises(
            TypeError, validate_environment_variables_from_Enum, "invalid_test_input"
        )

    def test_validate_environment_variables_from_Enum_raise_ValueError(
        self,
    ) -> None:
        os.environ[MockRequiredEnvVars.TEST_TWO.value] = (
            MockRequiredEnvVarsValues.TEST_TWO.value
        )

        self.assertRaises(
            ValueError, validate_environment_variables_from_Enum, MockRequiredEnvVars
        )

    def test_validate_environment_variables_from_Enum_returns_valid_mappings(
        self,
    ) -> None:
        os.environ[MockRequiredEnvVars.TEST_ONE.value] = (
            MockRequiredEnvVarsValues.TEST_ONE.value
        )
        os.environ[MockRequiredEnvVars.TEST_TWO.value] = (
            MockRequiredEnvVarsValues.TEST_TWO.value
        )

        expected_result: dict[str, str] = {
            MockRequiredEnvVars.TEST_ONE.value: MockRequiredEnvVarsValues.TEST_ONE.value,
            MockRequiredEnvVars.TEST_TWO.value: MockRequiredEnvVarsValues.TEST_TWO.value,
        }

        result: dict[str, str] = validate_environment_variables_from_Enum(
            MockRequiredEnvVars
        )

        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, expected_result)
