from datetime import datetime
import json

from pydantic import HttpUrl, BaseModel


class UpworkClient(BaseModel):
    """
    pydantic model to store client data
    """

    client_country: str
    client_city: str | None = None
    client_join_date: datetime
    client_jobs_posted: int | None = None
    client_hire_rate: float | None = None
    client_open_jobs: int | None = None
    client_total_spent: int | None = None
    client_total_hires: int | None = None
    client_active_hires: int | None = None
    client_avg_hourly_rate: float | None = None
    client_total_paid_hours: int | None = None


class UpworkJob(BaseModel):
    """
    Pydantic model to store job data
    """

    url: HttpUrl | None = None
    title: str
    posted_time: datetime
    full_description: str | None = None
    is_hourly: bool | None = None
    hourly_low: int | None = None
    hourly_high: int | None = None
    budget: int | None = None
    duration_months: int | None = None
    freelancer_experince_level: str | None = None
    project_type: str | None = None
    proposals: int = 0
    interviewing: int = 0
    invites_sent: int = 0
    unanswered_invites: int = 0


class PostingAttributes(BaseModel):
    job: UpworkJob
    client: UpworkClient


OPENAPI_SCHEMA = json.dumps(PostingAttributes.model_json_schema())
