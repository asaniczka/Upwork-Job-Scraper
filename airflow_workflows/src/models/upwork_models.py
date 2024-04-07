from datetime import datetime

from pydantic import HttpUrl, BaseModel


class ClientModel(BaseModel):
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


class JobModel(BaseModel):
    """
    Pydantic model to store job data
    """

    url: HttpUrl
    title: str
    posted_time: datetime
    description: str = ""
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
