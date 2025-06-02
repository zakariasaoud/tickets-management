import os

from dotenv import load_dotenv

load_dotenv()


def is_docker():
    return os.path.exists("/.dockerenv")


def get_database_url():
    # Local dev (not docker) or running tests: use in-memory sqlite database
    if not is_docker():
        return "sqlite+aiosqlite:///:memory:"

    # Docker app: use .env file or fallback
    db_path = os.getenv("SQLITE_DATABASE_PATH", "./data/app.db")
    return f"sqlite+aiosqlite:///{db_path}"


SQLITE_DATABASE_URL = get_database_url()
