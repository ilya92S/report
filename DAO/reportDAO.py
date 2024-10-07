import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from models import ReportModel
from schema import ReportResponse


@dataclass
class ReportDAO:

    db_session: Session

    async def save_to_db(self, report_data, inn, response_data):

        log_entry = ReportModel(
            full_name=report_data.full_name,
            email=report_data.email,
            request_id=str(report_data.UUID),
            report_name=report_data.report_name,
            inn=inn,
            response_data=dict(response_data)
        )
        self.db_session.add(log_entry)

        self.db_session.commit()
        self.db_session.refresh(log_entry)

    async def get_history_from_db(self, start_date: datetime, end_date: datetime) -> list[ReportResponse]:

        history = self.db_session.query(ReportModel).filter(
            ReportModel.created_at.between(start_date, end_date)
        )
        result = []
        for entry in history:

            if isinstance(entry.response_data, str):
                response_data = json.loads(entry.response_data)
            else:
                response_data = entry.response_data

            result.append(ReportResponse.model_validate(response_data))

        return result