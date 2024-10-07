from datetime import date
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class ReportModel(Base):
    __tablename__ = 'request_logs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    request_id: Mapped[str] = mapped_column(nullable=False)
    report_name: Mapped[str] = mapped_column(nullable=False)
    inn: Mapped[str] = mapped_column(nullable=False)
    response_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[date] = mapped_column(default=datetime.now(timezone.utc))
