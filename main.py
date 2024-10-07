from datetime import date
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Query

from dependency import get_report_service
from exception import AccessDeniedException, IncorrectINNException
from schema import ReportRequest, ReportResponse
from service import ReportService

app = FastAPI()


@app.post("/report", response_model=ReportResponse)
async def report(
        data: ReportRequest,
        report_service: Annotated[ReportService, Depends(get_report_service)]
):
    try:
        return await report_service.get_report(data)
    except AccessDeniedException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except IncorrectINNException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )


@app.get("/history")
async def get_history(
        report_service: Annotated[ReportService, Depends(get_report_service)],
        start_time: Annotated[date, Query(..., description="Начало даты поиска в формате YYYY-MM-DD")],
        end_time: Annotated[date, Query(..., description="Конец даты поиска в формате YYYY-MM-DD")]

):
    return await report_service.get_history(start_time, end_time)
