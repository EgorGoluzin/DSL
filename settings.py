from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)
    PROJECT_ROOT: Path
    TEST_WIRTH_RULE_PNG_SAVE: Path
    TEST_WIRTH_RULE_DOT_SAVE: Path
    TEST_GRAMMAR_OBJECT: Path


settings = Settings()
