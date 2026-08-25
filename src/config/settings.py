from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    # API Keys
    usda_api_key: str | None = Field(default=None, alias="USDA_API_KEY")

    # Database
    database_url: str = Field(
        default="sqlite:///data/ingredients.db", alias="DATABASE_URL"
    )

    # Vector Store
    chroma_persist_dir: str = Field(
        default="data/chroma", alias="CHROMA_PERSIST_DIR"
    )

    # App
    debug: bool = Field(default=False, alias="DEBUG")
    sql_echo: bool = Field(default=False, alias="SQL_ECHO")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173"], alias="CORS_ORIGINS"
    )
    agent_timeout_seconds: int = Field(
        default=300, alias="AGENT_TIMEOUT_SECONDS"
    )

    # LLM
    llm_model: str = Field(default="gemma4:31b-cloud", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    ollama_host: str = Field(
        default="http://localhost:11434", alias="OLLAMA_HOST"
    )
    ollama_api_key: str = Field(default="", alias="OLLAMA_API_KEY")

    # Embeddings
    embedding_model: str = Field(
        default="nomic-embed-text", alias="EMBEDDING_MODEL"
    )
    # Embeddings stay local by default; chat LLM may point at a cloud host.
    embedding_host: str = Field(
        default="http://localhost:11434", alias="EMBEDDING_HOST"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
