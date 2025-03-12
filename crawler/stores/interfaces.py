from abc import ABC, abstractmethod

from crawler.models.website import Website


class WebsiteDataStoreRecordKeepInterface(ABC):
    @abstractmethod
    def add_record(self, website: Website) -> None:
        """Add website to the desired data store"""
        raise NotImplementedError(
            f"{self.__class__.__name__} - add_record functionality is missing!"
        )


class WebsiteDataStoreRecordWriteInterface(ABC):
    write_success: bool = False

    @abstractmethod
    def write(self) -> None:
        """Writes all records from the Website to the desired data store"""
        raise NotImplementedError(
            f"{self.__class__.__name__} - write functionality is missing!"
        )


class WebsiteDataStoreKeepAndWriteInterface(
    WebsiteDataStoreRecordKeepInterface, WebsiteDataStoreRecordWriteInterface
):
    pass
