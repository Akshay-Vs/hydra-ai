import os
from pathlib import Path
from app.config.settings import settings
from app.utils.logging import create_logger
from sqlmodel import SQLModel, create_engine, Session, Field, select

logger = create_logger(__name__)

assert settings.database_url, (
    "DATABASE_URL must be set in the environment or .env file."
)
assert settings.tidb_ssl_ca, "TIDB_SSL_CA must be set in the environment or .env file."

DATABASE_URL = settings.database_url.replace(
    "<CA_PATH>", settings.tidb_ssl_ca.as_posix()
)

logger.info("Setting up database connection...")
engine = create_engine(DATABASE_URL)


def init_database():
    logger.info("Initializing database...")
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)


class Seed(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


def seed_database():
    with Session(engine) as session:
        if not session.exec(select(Seed)).first():
            logger.info("Seeding database with initial data.")
            session.add_all(
                [
                    Seed(name="Example Seed 1"),
                    Seed(name="Example Seed 2"),
                ]
            )
            session.commit()
        else:
            logger.info("Database already seeded with initial data.")


def get_session():
    with Session(engine) as session:
        yield session
