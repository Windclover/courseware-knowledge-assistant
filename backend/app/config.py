from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _parse_cors_origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "课件智能知识点提取助手"
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")
    qwen_base_url: str = os.getenv(
        "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    qwen_model: str = os.getenv("QWEN_MODEL", "qwen-turbo")
    cors_origins: tuple[str, ...] = _parse_cors_origins()
    cors_origin_regex: str = os.getenv(
        "CORS_ORIGIN_REGEX", r"http://(127\.0\.0\.1|localhost):\d+"
    )
    root_dir: Path = ROOT_DIR
    database_path: Path = ROOT_DIR / "data" / "app.db"
    upload_root: Path = ROOT_DIR / "data" / "uploads"
    output_root: Path = ROOT_DIR / "data" / "outputs"
    max_upload_size_mb: int = 30
    retrieval_limit: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
