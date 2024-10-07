from fastapi import Depends

from DAO.reportDAO import ReportDAO
from database import get_db_session, SessionLocal
from service import ReportService
from settings import Settings


def get_report_dao(
        db_session: SessionLocal = Depends(get_db_session)
) -> ReportDAO:
    return ReportDAO(db_session)


def get_report_service(

        db_session: SessionLocal = Depends(get_report_dao)
) -> ReportService:
    return ReportService(db_session=db_session, settings=Settings())
