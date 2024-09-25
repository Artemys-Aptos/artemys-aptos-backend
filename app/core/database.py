from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from contextlib import contextmanager

from app.core.constants import SQLALCHEMY_DATABASE_URL

from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=1000,  # Adjust based on your app's concurrency requirements
    max_overflow=500,  # Allows for extra connections in times of high demand
    pool_timeout=120,  # Reduces wait time for a connection
    pool_recycle=36000,  # Recycles connections every 1 hours
    # echo_pool='debug',  # Logs pool checkouts/checkins (remove in production)
    pool_pre_ping=True,
    # Any idle transaction request past 20seconds will be terminated
    # connect_args={"options": "-c idle_in_transaction_session_timeout=20000"},
)


def get_session():
    with Session(engine) as session:
        yield session


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session_with_ctx_manager():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
