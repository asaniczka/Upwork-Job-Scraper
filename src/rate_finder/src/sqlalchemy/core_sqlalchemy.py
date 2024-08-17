import os

from rich import print
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

from src.models.db_models import Base

engine = create_engine(os.environ["POSTGRES_URL"])

Base.metadata.create_all(engine)
SESSIONMAKER = sessionmaker(engine)
