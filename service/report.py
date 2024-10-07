import asyncio
from dataclasses import dataclass
from datetime import date

import httpx

from DAO import reportDAO
from exception import AccessDeniedException, IncorrectINNException
from settings import Settings
from schema import ReportResponse, ReportRequest


@dataclass
class ReportService:
    db_session: reportDAO
    settings: Settings()

    async def fetch_basic_info(self, inn):

        url = "https://focus-api.kontur.ru/api3/req"
        params = {
            "key": self.settings.TEST_KEY,
            "inn": inn,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 403:
                raise IncorrectINNException
            elif response.status_code == 400:
                raise AccessDeniedException(detail=response.text)

            response.raise_for_status()
            return response.json()

    async def fetch_taxes(self, inn):

        url = "https://focus-api.kontur.ru/api3/taxes"
        params = {
            "key": self.settings.TEST_KEY,
            "inn": inn,
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(url, params=params)
            if response.status_code == 403:
                raise IncorrectINNException
            elif response.status_code == 400:

                raise AccessDeniedException(detail=response.text)

            response.raise_for_status()
            return response.json()

    async def fetch_gov_purchases(self, inn):
        url = "https://focus-api.kontur.ru/api3/govPurchasesOfCustomer"
        params = {
            "key": self.settings.TEST_KEY,
            "inn": inn,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 403:
                raise IncorrectINNException
            elif response.status_code == 400:

                raise AccessDeniedException(detail=response.text)

            response.raise_for_status()
            return response.json()

    @staticmethod
    async def purchases(gov_purchases: list):
        total_sum = 0
        total_count = 0

        for i in gov_purchases[0]["purchasesOfCustomer"]:
            """
            Не совсем понятны условия, закупка должна быть завершена или размещена, или то и другое.
            """
            if i["purchaseStateDescription"] == "Контракт заключен" and i["contractStage"] == "execution":
                total_sum += i["contractPrice"]["sum"]
                total_count += 1

        if total_sum == 0:
            total_sum = None
        else:
            total_sum = round(total_sum, 2)
        if total_count == 0:
            total_count = None

        return total_sum, total_count

    async def get_ul_data(self, data: ReportRequest):
        inn = data.inn
        basic_info_task = asyncio.create_task(self.fetch_basic_info(inn))

        gov_purchases = asyncio.create_task(self.fetch_gov_purchases(inn))

        try:
            """
            Если будут данные по налогам, в случае ошибок
            данные записываем как None.
            """
            taxes_task = asyncio.create_task(self.fetch_taxes(inn))
            taxes = await taxes_task
            taxes = {
                "yearly_info": taxes[0].get("year_info", None),
                "total_sum": taxes[0].get("total_sum", None)
            }
        except (IncorrectINNException, AccessDeniedException):
            taxes = {
                "yearly_info": None,
                "total_sum": None
            }

        basic_info = await basic_info_task
        ul_info = basic_info[0].get("UL", {})
        gov_purchases = await gov_purchases

        total_sum, total_count = await self.purchases(gov_purchases=gov_purchases)

        response_data = ReportResponse(
            full_name=data.full_name,
            email=data.email,
            UUID=data.UUID,
            report_name=data.report_name,
            basic_info={
                "name": ul_info.get("legalName", {}).get("short", None),
                "kpp": ul_info.get("kpp", None),
                "okpo": ul_info.get("okpo", None),
                "okato": ul_info.get("okato", None),
                "okfs": ul_info.get("okfs", None),
                "okogu": ul_info.get("okogu", None),
                "okopf": ul_info.get("okopf", None),
                "opf": ul_info.get("opf", None),
                "oktmo": ul_info.get("oktmo", None),
                "registration_date": ul_info.get("registrationDate", None),
            },
            contact_info={
                "phones": basic_info[0].get('contactPhones', {}).get('count', None),
                "websites": None
            },
            gov_purchases={
                "total_sum": total_sum,
                "total_count": total_count
            },
            taxes={
                "yearly_info": taxes.get("yearly_info", None),
                "total_sum": taxes.get("total_sum", None)
            }
        )

        await self.db_session.save_to_db(data, data.inn, response_data)
        return response_data

    async def get_ip_data(self, data: ReportRequest) -> ReportResponse:
        inn = data.inn
        print(type(inn), inn)
        basic_info_task = asyncio.create_task(self.fetch_basic_info(inn))
        gov_purchases_task = asyncio.create_task(self.fetch_gov_purchases(inn))

        try:
            """
            Если будут данные по налогам, в случае ошибок
            данные записываем как None.
            """
            taxes_task = asyncio.create_task(self.fetch_taxes(inn))
            taxes = await taxes_task
            taxes = {
                "yearly_info": taxes[0].get("year_info", None),
                "total_sum": taxes[0].get("total_sum", None)
            }
        except (IncorrectINNException, AccessDeniedException):
            taxes = {
                "yearly_info": None,
                "total_sum": None
            }
        gov_purchases = await gov_purchases_task
        basic_info = await basic_info_task

        total_sum, total_count = await self.purchases(gov_purchases=gov_purchases)

        response_data = ReportResponse(
            full_name=data.full_name,
            email=data.email,
            UUID=data.UUID,
            report_name=data.report_name,
            basic_info={
                "name": basic_info[0].get("IP", {}).get("fio", None),
                "kpp": basic_info[0].get("IP", {}).get("kpp", None),
                "okpo": basic_info[0].get("IP", {}).get("okpo", None),
                "okato": basic_info[0].get("IP", {}).get("okato", None),
                "okfs": basic_info[0].get("IP", {}).get("okfs", None),
                "okogu": basic_info[0].get("IP", {}).get("okogu", None),
                "okopf": basic_info[0].get("IP", {}).get("okopf", None),
                "opf": basic_info[0].get("IP", {}).get("opf", None),
                "oktmo": basic_info[0].get("IP", {}).get("oktmo", None),
                "registration_date": basic_info[0].get("IP", {}).get("registrationDate", None),
            },
            contact_info={
                "phones": basic_info[0].get("IP", {}).get("contactPhones", {}),
                "websites": None
            },
            gov_purchases={
                "total_sum": total_sum,
                "total_count": total_count  # не понятно откуда брать
            },
            taxes={
                "yearly_info": taxes.get("yearly_info"),
                "total_sum": taxes.get("total_sum")
            }
        )
        await self.db_session.save_to_db(data, data.inn, response_data)
        return response_data

    async def get_report(self, data: ReportRequest):
        if len(str(data.inn)) == 10:
            return await self.get_ul_data(data=data)

        elif len(str(data.inn)) == 12:
            return await self.get_ip_data(data=data)

    async def get_history(self, start_date: date, end_date: date):
        return await self.db_session.get_history_from_db(start_date=start_date, end_date=end_date)
