import os
from unittest import TestCase


class ExamplesTest(TestCase):
    def setUp(self):
        folder_all_tests: str = "tests"
        folder_all_examples: str = "examples"

        self.full_path_to_example_folder: str = os.path.join(
            folder_all_tests, folder_all_examples
        )

        return super().setUp()
