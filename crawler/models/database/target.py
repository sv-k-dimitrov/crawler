from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .base import Base


class Target(Base):
    __tablename__ = "targets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="this will be used as filename",
    )
    crawling_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    created_at = Column(DateTime, server_default=func.now())
    website = Column(String(256), nullable=False, comment="this is the root URL")
    s3_bucket = Column(String(256), nullable=True)
    s3_location = Column(String(256), nullable=True)
    filesystem_location = Column(String(256), nullable=True)
    website_metadata = Column(
        JSON,
        nullable=True,
        comment="example location usage for dun number or any other valuable information",
    )
    count_pdf_pages = Column(Integer, default=0)
    count_html_pages = Column(Integer, default=0)
    largest_pdf_size = Column(Integer, default=0)
    largest_pdf_link = Column(String(256), nullable=True)

    target = relationship("Page", back_populates="target")
    crawling_job = relationship("Job", back_populates="targets")

    finished_at = Column(DateTime, nullable=True)

    def set_finished(self, session):
        """Sets the finished timestamp to the current UTC time from the database server."""
        self.finished_at = session.execute(select(func.now())).scalar()
        session.commit()
