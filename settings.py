from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    TEST_KEY: str = ""

    class Config:
        env_file = ".env"