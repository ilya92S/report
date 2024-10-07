from dataclasses import dataclass

from fastapi import status

class AccessDeniedException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        self.detail = detail
        self.status_code = status_code

@dataclass
class IncorrectINNException(Exception):
    status_code=status.HTTP_403_FORBIDDEN
    detail="Некорректный ИНН"