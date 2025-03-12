from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj
