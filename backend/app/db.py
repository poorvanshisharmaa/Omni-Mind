from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


def init_db() -> None:
    from app import models  # noqa: F401  (ensure models are registered before create_all)

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
