""""""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import UniqueConstraint


class Base(DeclarativeBase):
    pass


class DBUpworkContracts(Base):
    __tablename__ = "upwork_contracts"

    job_id: Mapped[str] = mapped_column(primary_key=True)
    is_fake_job_id: Mapped[bool]
    job_title: Mapped[str]
    start_date: Mapped[datetime]
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_days: Mapped[Optional[int]] = mapped_column(nullable=True)
    freelancer_name: Mapped[str]
    freelancer_id: Mapped[str]
    is_fake_freelancer_id: Mapped[bool]
    total_hours: Mapped[float]
    total_paid: Mapped[float]
    hourly_rate: Mapped[Optional[float]] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "job_title",
            "freelancer_id",
            name="unique_upwork_contracts_jobtitle_freelancerid",
        ),
    )
