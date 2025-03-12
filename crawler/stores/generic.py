from dataclasses import dataclass, field

from crawler.models.website import Website

from .interfaces import WebsiteDataStoreRecordKeepInterface


@dataclass
class _StoreDataRecords(WebsiteDataStoreRecordKeepInterface):
    data: list[Website] = field(init=False, default_factory=list)

    def add_record(self, website: Website) -> None:
        if not isinstance(website, Website):
            raise TypeError(
                f"{self.__class__.__name__} - invalid type for input parameter!"
            )

        self.data.append(website)
