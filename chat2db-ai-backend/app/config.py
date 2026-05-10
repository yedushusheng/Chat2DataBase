"""
统一配置管理模块
支持 .env + yaml 双配置源，环境变量优先
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "development")
env_file = Path(__file__).resolve().parent.parent / f".env.{ENV}" if ENV != "development" else Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)


class Settings(BaseSettings):
    """应用配置类"""

    APP_NAME: str = "Chat2DB-AI"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_DIR: str = "./logs"

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_COLLECTION: str = "db_knowledge"

    SELF_DB_NAME: str = "SelfDB"
    SELF_DB_IDENTIFIERS: List[str] = ["自研", "selfdb"]

    DOUBAO_API_KEY: str = ""
    DOUBAO_MODEL: str = ""
    DOUBAO_BASE_URL: str = ""

    WENXIN_API_KEY: str = ""
    WENXIN_SECRET_KEY: str = ""
    WENXIN_MODEL: str = ""

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = ""
    DEEPSEEK_BASE_URL: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    OPENAI_BASE_URL: str = ""

    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = ""
    CLAUDE_BASE_URL: str = ""

    ROUTER_STRATEGY: str = "priority"
    EXTERNAL_MODEL_PRIORITY: List[str] = ["deepseek", "doubao", "wenxin", "openai"]
    FALLBACK_ENABLED: bool = True

    MAX_UPLOAD_SIZE: int = 52428800
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt", "md"]
    UPLOAD_DIR: str = "./uploads"

    CONVERSATION_STORE: str = "sqlite"
    CONVERSATION_DB_PATH: str = "./conversations.db"

    SQL_CHECK_ENABLED: bool = True
    SQL_DANGEROUS_KEYWORDS: List[str] = ["drop", "delete", "truncate", "shutdown"]

    _yaml_config: Dict[str, Any] = {}

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_yaml()

    def _load_yaml(self):
        yaml_path = Path(__file__).resolve().parent.parent / f"config.{ENV}.yaml"
        if not yaml_path.exists():
            yaml_path = Path(__file__).resolve().parent.parent / "config.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                self._yaml_config = yaml.safe_load(f) or {}

    def get_yaml(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._yaml_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    @property
    def databases(self) -> List[Dict[str, Any]]:
        return self.get_yaml("databases", [])

    @property
    def agents_config(self) -> Dict[str, Any]:
        return self.get_yaml("agents", {})

    @property
    def rag_config(self) -> Dict[str, Any]:
        return self.get_yaml("rag", {})

    @property
    def mcp_config(self) -> Dict[str, Any]:
        return self.get_yaml("mcp", {})

    @property
    def skills_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent / self.get_yaml("skills.base_dir", "./skills_data")


settings = Settings()
