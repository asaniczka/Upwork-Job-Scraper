""""""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, AliasChoices, AliasPath, Field, model_validator


class PastJob(BaseModel):
    job_id: str | None = Field(validation_alias=AliasPath("jobInfo", "ciphertext"))
    is_fake_job_id: bool = False
    job_title: str = Field(validation_alias=AliasPath("jobInfo", "title"))
    start_date: datetime | None = Field(validation_alias=AliasPath("startDate"))
    end_date: datetime | None = Field(validation_alias=AliasPath("endDate"))
    duration_days: int | None = None
    freelancer_name: str = Field(
        validation_alias=AliasPath("contractorInfo", "contractorName")
    )
    freelancer_id: str | None = Field(
        validation_alias=AliasPath("contractorInfo", "ciphertext")
    )
    is_fake_freelancer_id: bool = False
    total_hours: float = Field(validation_alias=AliasPath("totalHours"))
    total_paid: float = Field(validation_alias=AliasPath("totalCharge"))
    hourly_rate: float | None = Field(
        validation_alias=AliasChoices(AliasPath("rate", "amount"), AliasPath("rate"))
    )

    @model_validator(mode="after")
    def _validate_id(self):

        if not self.job_id:
            self.job_id = str(uuid4())
            self.is_fake_job_id = True

        if not self.freelancer_id:
            self.freelancer_id = str(uuid4())
            self.is_fake_freelancer_id = True

        return self

    @model_validator(mode="after")
    def _count_contract_days(self):

        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            self.duration_days = duration.days

        return self


class WorkHistory(BaseModel):
    work_history: list[PastJob] = Field(validation_alias=AliasPath("workHistory"))
