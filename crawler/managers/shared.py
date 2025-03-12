from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from crawler.models.database import Base, Job, Page, Target  # noqa: F401

from .utils import validate_environment_variables_from_Enum


class RequiredEnvironmentVariables(str, Enum):
    DATABASE_HOST: str = "DATABASE_HOST"
    DATABASE_USER: str = "DATABASE_USER"
    DATABASE_PASSWORD: str = "DATABASE_PASSWORD"
    DATABASE_PORT: str = "DATABASE_PORT"
    DATABASE_NAME: str = "DATABASE_NAME"


@dataclass
class CrawlingDatabaseSetupValidations:
    database_connection_string: str = field(init=False)

    def __post_init__(self) -> None:
        mappings: dict[str, str] = validate_environment_variables_from_Enum(
            RequiredEnvironmentVariables
        )

        user: str = mappings.get(RequiredEnvironmentVariables.DATABASE_USER.value)
        password: str = mappings.get(
            RequiredEnvironmentVariables.DATABASE_PASSWORD.value
        )
        host: str = mappings.get(RequiredEnvironmentVariables.DATABASE_HOST.value)
        port: str = mappings.get(RequiredEnvironmentVariables.DATABASE_PORT.value)
        database: str = mappings.get(RequiredEnvironmentVariables.DATABASE_NAME.value)

        self.database_connection_string: str = (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )


@dataclass
class CrawlingDatabaseSetup(CrawlingDatabaseSetupValidations):
    database_engine: Engine = field(init=False)
    session: Session = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.database_engine = create_engine(self.database_connection_string)
        Base.metadata.create_all(self.database_engine)

        session_maker: sessionmaker = sessionmaker(bind=self.database_engine)
        self.session: Session = session_maker()


def create_job(crawl_depth: int) -> UUID:
    db_setup: CrawlingDatabaseSetup = CrawlingDatabaseSetup()

    job_instance = Job(
        depth=crawl_depth,
    )
    db_setup.session.add(job_instance)
    db_setup.session.commit()

    return job_instance.id


def finish_job(job_uuid: UUID):
    db_setup: CrawlingDatabaseSetup = CrawlingDatabaseSetup()

    job_instance: Job = db_setup.session.query(Job).filter_by(id=job_uuid).first()

    if not job_instance:
        raise ValueError(f"finish_job - unable to find Job with id: {job_uuid}")

    job_instance.set_finished(db_setup.session)
