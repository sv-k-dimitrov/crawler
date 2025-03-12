from sqlalchemy import Column, DateTime, Index, Integer, func
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    created_at = Column(DateTime, server_default=func.now())
    finished = Column(DateTime, nullable=True)
    status = Column(
        ENUM("created", "running", "failed", name="status"),
        default="running",
        nullable=False,
    )
    depth = Column(Integer, nullable=False)

    targets = relationship("Target", back_populates="crawling_job")

    @hybrid_property
    def is_finished(self):
        """Returns True if the job has a finished timestamp set."""
        return self.finished is not None

    def set_finished(self, session):
        """Sets the finished timestamp to the current UTC time from the database server."""
        self.finished = session.execute(select(func.now())).scalar()
        self.status = "created"
        session.commit()


Index("crawling_job_status", Job.status)
