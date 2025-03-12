from abc import ABC, abstractmethod

from crawler.models.website import Website


class WebsiteModelReader(ABC):
    @abstractmethod
    def read(self, full_path_to_file: str) -> Website:
        raise NotImplementedError("WebsiteModelReader.read - missing implementation")
