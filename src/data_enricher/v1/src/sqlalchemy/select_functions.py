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

    print("Getting freelancer from db")
    with SESSIONMAKER() as session:

        db_freelancer = (
            session.query(DBFreelancerIdentity)
            .filter(DBFreelancerIdentity.did_scrape != True)
            .first()
        )
        if db_freelancer:
            return db_freelancer.cipher
        return None


def get_batch_freelancers_from_db(limit=10) -> list[str] | None:

    print(f"Getting {limit} freelancers from db")
    with SESSIONMAKER() as session:

        db_freelancers = (
            session.query(DBFreelancerIdentity)
            .filter(DBFreelancerIdentity.did_scrape != True)
            .limit(limit)
            .all()
        )
        if db_freelancers:
            return [x.cipher for x in db_freelancers]
        return None


if __name__ == "__main__":
    get_batch_freelancers_from_db()