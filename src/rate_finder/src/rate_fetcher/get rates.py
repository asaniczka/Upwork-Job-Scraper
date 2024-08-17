""""""

# pylint: disable = wrong-import-position
from wrapworks.files import load_json
from wrapworks import cwdtoenv
from rich import print
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
cwdtoenv()

from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER
from src.models.job_models import WorkHistory
from src.models.db_models import DBUpworkContracts


raw_data = load_json("src/temp/sample.json")
work_history = WorkHistory(**raw_data)

with SESSIONMAKER() as session:
    for i in work_history.work_history:
        job = i.model_dump()
        job = DBUpworkContracts(**job)
        session.merge(job)

    session.commit()
