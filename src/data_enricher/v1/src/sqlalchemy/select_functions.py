""""""

from rich import print
from wrapworks import cwdtoenv
from dotenv import load_dotenv

cwdtoenv()
load_dotenv()

from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER
from src.models.db_models import DBFreelancerIdentity


def get_freelancer_from_db() -> str | None:
    """"""

    print("Getting freelancer to db")
    with SESSIONMAKER() as session:

        db_freelancer = session.query(DBFreelancerIdentity).first()
        if db_freelancer:
            return db_freelancer.cipher
        return None


if __name__ == "__main__":
    get_freelancer_from_db()
