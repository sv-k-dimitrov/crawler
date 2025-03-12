import hashlib
from enum import Enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import relationship

from .base import Base

page_type_enum = ENUM("HTML", "PDF", name="page_types")
page_content_type_enum = ENUM(
    "TEXT",
    "TEXT/unicode",
    "UNKNOWN",
    "HTML/unparsed",
    "XML/unparsed",
    "JSON/unparsed",
    name="page_content_types",
)


class PageTypes(str, Enum):
    HTML: str = "HTML"
    PDF: str = "PDF"


class PageContentTypes(str, Enum):
    TEXT: str = "TEXT"
    TEXT_unicode: str = "TEXT/unicode"
    UNKNOWN: str = "UNKNOWN"
    HTML_UNPARSED: str = "HTML/unparsed"
    XML_UNPARSED: str = "XML/unparsed"
    JSON_UNPARSED: str = "JSON/unparsed"


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id"))
    page_type = Column(page_type_enum, nullable=False)
    page_content_type = Column(page_content_type_enum, nullable=False)
    _website = Column(
        "website",
        String(256),
        nullable=True,
        comment="Full URL of the page which was scraped",
    )
    website_hash = Column(
        String(64),
        nullable=False,
        unique=False,
        comment="SHA256 hash of the website URL",
    )
    has_title = Column(Boolean, nullable=False)
    has_content = Column(Boolean, nullable=False)

    min_word_length = Column(Integer, nullable=True)
    mean_word_length = Column(Integer, nullable=True)
    max_word_length = Column(Integer, nullable=True)

    min_sentence_length = Column(Integer, nullable=True)
    mean_sentence_length = Column(Integer, nullable=True)
    max_sentence_length = Column(Integer, nullable=True)

    target = relationship("Target", back_populates="target")

    def __repr__(self) -> str:
        if not self.id:
            return f"{self.__class__.__name__} - website: {self.website}"

        return f"{self.__class__.__name__} - id: {self.id}, website: {self.website}"

    @property
    def website(self):
        """Getter for the website property."""
        if self._website:
            return self._website
        elif self.website_hash:
            # Optionally reconstruct the URL if a decoding mechanism exists
            return f"[HASHED_URL:{self.website_hash}]"
        return None

    @website.setter
    def website(self, value):
        """Setter for the website property."""
        if value and len(value) > 256:
            # Too long, store only the hash and leave _website empty
            self._website = None
            self.website_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
        elif value:
            # Valid website, store both the value and its hash
            self._website = value
            self.website_hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
        else:
            # Handle case where the value is None
            self._website = None
            self.website_hash = None
