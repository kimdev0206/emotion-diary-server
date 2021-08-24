from typing import Dict
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml


def load_config(file) -> Dict:
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data


DB_FILE = load_config(Path(__file__).parent.parent / "etc" / "db.yaml")
db = {**DB_FILE["main"]}
MYSQL_URL = f"mysql+pymysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['db']}?charset={db['charset']}"

engine = create_engine(
    MYSQL_URL,
    echo=True,
    pool_recycle=25000,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()