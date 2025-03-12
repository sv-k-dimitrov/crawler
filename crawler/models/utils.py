import json
import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from lxml import etree

from .database.page import PageContentTypes

# from xml.etree import ElementTree as ET


@dataclass
class TextStatistics:
    min_word_length: int = field(default=None)
    mean_word_length: int = field(default=None)
    max_word_length: int = field(default=None)

    min_sentence_length: int = field(default=None)
    mean_sentence_length: int = field(default=None)
    max_sentence_length: int = field(default=None)


def calculate_text_statistics(text: str) -> TextStatistics:
    text_stats: TextStatistics = TextStatistics()

    # Split text into sentences using a regex
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    sentence_lengths = [
        len(sentence.strip()) for sentence in sentences if sentence.strip()
    ]

    # Split text into words
    words = re.findall(r"\b\w+\b", text)
    word_lengths = [len(word) for word in words]

    text_stats.min_sentence_length = min(sentence_lengths) if sentence_lengths else None
    text_stats.mean_sentence_length = (
        sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else None
    )
    text_stats.max_sentence_length = max(sentence_lengths) if sentence_lengths else None

    text_stats.min_word_length = min(word_lengths) if word_lengths else None
    text_stats.mean_word_length = (
        sum(word_lengths) / len(word_lengths) if word_lengths else None
    )
    text_stats.max_word_length = max(word_lengths) if word_lengths else None

    if text_stats.mean_word_length is not None:
        text_stats.mean_word_length = int(text_stats.mean_word_length)

    if text_stats.mean_sentence_length is not None:
        text_stats.mean_sentence_length = int(text_stats.mean_sentence_length)

    return text_stats


def detect_page_content_type(text: str) -> PageContentTypes:
    try:
        # Check if it's JSON
        json.loads(text)
        return PageContentTypes.JSON_UNPARSED
    except json.JSONDecodeError:
        pass

    try:
        # Check if it's HTML
        soup = BeautifulSoup(text, "html.parser")
        if text.find("<?xml") == -1 and (
            soup.find("html") or soup.find("div") or soup.find("span")
        ):
            return PageContentTypes.HTML_UNPARSED
    except Exception:
        pass

    try:
        # Check if it's XML
        if text.find("<?xml") != -1:
            text = text.encode("utf-8")
        etree.fromstring(text)
        return PageContentTypes.XML_UNPARSED
    except etree.XMLSyntaxError:
        pass

    text = re.sub(r"\s+", "", text)
    # Check if it contains only plain text
    if (
        isinstance(text, str)
        and text.isprintable()
        and text.find("<") == -1
        and text.find("{") == -1
    ):
        # Unicode text will pass here as well
        return (
            PageContentTypes.TEXT if text.isascii() else PageContentTypes.TEXT_unicode
        )

    # If none of the above, classify as UNKNOWN
    return PageContentTypes.UNKNOWN
