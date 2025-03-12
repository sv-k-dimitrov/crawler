import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from crawler.models.website import Website

from .generic import _StoreDataRecords
from .interfaces import WebsiteDataStoreRecordWriteInterface

logger: logging.Logger = logging.getLogger(__name__)


class FileType(str, Enum):
    JSON: str = ".json"


@dataclass
class FileSystemDataStore(_StoreDataRecords, WebsiteDataStoreRecordWriteInterface):
    file_name: str
    directory_path: str
    format: FileType
    raise_error_if_file_exists: bool = field(default=False)
    full_path_to_file: str = field(init=False)
    full_path_to_file_without_extension: str = field(init=False)
    data_content: list[dict[str, Any]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if (
            not isinstance(self.file_name, str)
            or not isinstance(self.directory_path, str)
            or not isinstance(self.format, FileType)
        ):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter!"
            )

        if not self.file_name or not self.directory_path:
            raise ValueError(
                f"{self.__class__.__name__} - invalid value for required string parameters!"
            )

        if not os.path.isdir(self.directory_path):
            raise IsADirectoryError(
                f"{self.__class__.__name__} - '{self.directory_path}' it's not a directory"
            )

        if not os.path.exists(self.directory_path):
            raise OSError(
                f"{self.__class__.__name__} - '{self.directory_path}' wasn't found"
            )

        self.full_path_to_file = os.path.join(
            self.directory_path, self.file_name + self.format.value
        )
        self.full_path_to_file_without_extension = os.path.join(
            self.directory_path, self.file_name
        )

        if os.path.exists(self.full_path_to_file) and self.raise_error_if_file_exists:
            raise OSError(
                f"{self.__class__.__name__} - file '{self.full_path_to_file}' already exists. Disable 'raise_error_if_file_exists' and run again to allow dynamic management of the end file."
            )

        counter: int = 0
        while True:
            if counter > 0:
                self.full_path_to_file = os.path.join(
                    self.directory_path,
                    f"{self.file_name}_{counter}" + self.format.value,
                )
                self.full_path_to_file_without_extension = os.path.join(
                    self.directory_path, f"{self.file_name}_{counter}"
                )

            if os.path.exists(self.full_path_to_file):
                logger.warning(
                    f"{self.__class__.__name__} - file '{self.full_path_to_file}' already exists!"
                )
            else:
                break

            counter += 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}, full path to file: {self.full_path_to_file}"

    def _generate_content(self) -> None:
        website: Website
        for website in self.data:
            self.data_content.append(website.to_json())

    def write(self) -> None:
        self._generate_content()

        if self.format == FileType.JSON:
            logger.info(
                f"{self.__class__.__name__} - writing extracted content to: {self.full_path_to_file}"
            )
            with open(self.full_path_to_file, "w") as json_file:
                json.dump(self.data_content, json_file, indent=4)

        self.write_success = True
