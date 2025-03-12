from unittest import TestCase
from unittest.mock import MagicMock, patch

from crawler.stores.aws import AwsDataStore
from tests.fabrics.test_website import WebsiteFabric


class MockedS3Client:
    def put_object(*args, **kwargs) -> None:
        return None


class TestAwsDataStore(WebsiteFabric):
    @patch.object(AwsDataStore, "__post_init__", return_value=None)
    def test_filename_sets_json_extension_on_write(
        self,
        aws_data_store_post_init_mock: MagicMock,
    ) -> None:
        aws_data_store: AwsDataStore = AwsDataStore("example_s3_bucket")
        aws_data_store._s3_client = MockedS3Client()

        aws_data_store.add_record(self.website_empty)

        aws_data_store.write()

        self.assertEqual(True, aws_data_store.filename.endswith(".json"))

    @patch.object(AwsDataStore, "__post_init__", return_value=None)
    def test_on_write_update_write_success_property(
        self,
        aws_data_store_post_init_mock: MagicMock,
    ) -> None:
        aws_data_store: AwsDataStore = AwsDataStore("example_s3_bucket")
        aws_data_store._s3_client = MockedS3Client()

        aws_data_store.add_record(self.website_empty)

        aws_data_store.write()

        self.assertEqual(True, aws_data_store.write_success)
