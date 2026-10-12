from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Server & Environment
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    STANDALONE_LOCAL_MODE: bool = True
    OFFLINE_DEMO_MODE: bool = True

    # LLM Settings
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 4000
    LLM_SEND_RAW_CODE: bool = False

    # Datastores
    DATABASE_URL: str = "sqlite:///./data/modernrx.db"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "modernrx_secret"
    USE_NEO4J: bool = False

    REDIS_URL: str = "redis://localhost:6379/0"
    USE_CELERY: bool = False

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "modernrx-artifacts"
    USE_S3: bool = False

    # Auth & Security
    JWT_SECRET: str = "modernrx-super-secure-jwt-signing-secret-key-32chars"
    JWT_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Algorithm Weights & Multipliers
    DECOMP_WEIGHTS: str = "0.30,0.20,0.25,0.10,0.15"
    DECOMP_GAMMA: float = 1.5
    HDBSCAN_MIN_CLUSTER_SIZE: int = 4
    MONTECARLO_RUNS: int = 10000
    GXP_MULTIPLIER_HIGH: float = 1.8
    GXP_MULTIPLIER_MEDIUM: float = 1.3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def weights_list(self) -> List[float]:
        return [float(w.strip()) for w in self.DECOMP_WEIGHTS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
