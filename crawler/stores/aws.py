import logging
from dataclasses import dataclass, field
from typing import Any

import boto3
from mypy_boto3_s3.client import S3Client

from crawler.models.website import Website

from .generic import _StoreDataRecords
from .interfaces import WebsiteDataStoreRecordWriteInterface

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class AwsDataStore(_StoreDataRecords, WebsiteDataStoreRecordWriteInterface):
    s3_bucket_name: str
    filename: str = field(default=None)
    _s3_client: S3Client = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.s3_bucket_name, str):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter, expecting string!"
            )

        self._s3_client = boto3.client("s3")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} , S3 bucket: {self.s3_bucket_name}, DynamoDB table: {self.dynamodb_table_name}"

    def write(self) -> None:
        if not self.filename:
            self.filename = f"{self.data[0].safe_key}.json"

        if self.filename and not self.filename.endswith(".json"):
            self.filename = f"{self.filename}.json"

        website: Website
        for website in self.data:
            website_content: dict[str, Any] = website.to_json()

            self._s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=self.filename,
                Body=website_content,
                ContentType="application/json",
            )

            logger.info(
                f"{self.__class__.__name__} - {self.filename} completed write to S3 bucket {self.s3_bucket_name}"
            )

        self.write_success = True
