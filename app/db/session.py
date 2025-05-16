from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

from app.core.config import DATABASE_URL

# Apply check_same_thread only for SQLite
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, 
    # not required using postgresql
    # connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# # sqlite database foreign key constraints enabling logic
# @event.listens_for(engine, "connect")
# def enable_sqlite_fks(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON;")
#     cursor.close()