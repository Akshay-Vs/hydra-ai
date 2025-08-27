from contextlib import contextmanager
from typing import List, Type

from app.config.settings import settings
from app.models.sql_model import AgentMemory, Incident, Log, Metric
from app.utils.logging import create_logger
from sqlmodel import SQLModel, create_engine, Session, Field, select, text
from sqlalchemy_schemadisplay import create_schema_graph

logger = create_logger(__name__)

assert settings.database_url, (
    "DATABASE_URL must be set in the environment or .env file."
)
assert settings.tidb_ssl_ca, "TIDB_SSL_CA must be set in the environment or .env file."

DATABASE_URL = settings.database_url.replace(
    "<CA_PATH>", settings.tidb_ssl_ca.as_posix()
)

logger.info("Setting up database connection...")
engine = create_engine(DATABASE_URL, echo=settings.debug)


def init_database():
    logger.info("Initializing database...")
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Enable HTAP for specified tables
    enable_HTAP(htap_tables=[Incident, Log, Metric, AgentMemory])

    # Render the database schema to a dot file
    render_db()


def enable_HTAP(htap_tables: List[Type[SQLModel]]):
    with engine.connect() as conn:
        for table in htap_tables:
            tablename = table.__tablename__
            try:
                conn.execute(text(f"ALTER TABLE {tablename} SET TIFLASH REPLICA 1"))
                logger.info(f"Enabled TiFlash replica for `{tablename}` table.")
            except Exception as e:
                logger.warning(f"Could not enable TiFlash for {tablename}: {e}")
        conn.commit()


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


def render_db():
    if not settings.debug:
        logger.warning("Skipping database schema rendering in non-debug mode.")
        return

    logger.info("Rendering database schema...")
    graph = create_schema_graph(
        engine=engine,
        metadata=SQLModel.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir="LR",
    )

    graph.write("database_schema.dot")
    logger.info("Database schema rendered to 'database_schema.dot'.")


@contextmanager
def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error during database session: {e}")
            session.rollback()
            raise e
