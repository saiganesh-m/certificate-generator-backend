from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# 1. Handle SQLite Threading
# SQLite by default only allows the thread that created the connection to communicate with it.
# Because FastAPI handles requests across multiple async worker threads,
# SQLite requires "check_same_thread": False.
# Note: When deploying to MySQL, connect_args remains empty because MySQL supports multi-threading natively!
connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # MySQL / MariaDB / PostgreSQL Connection Pooling
    # pool_recycle=3600 prevents MySQL server 'MySQL server has gone away' timeout errors
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
    })

# 2. Create the Database Engine
# pool_pre_ping=True tests the connection before using it.
# If MySQL or SQLite dropped the connection, it silently reconnects instead of crashing!
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# 3. Create the Session Factory
# autocommit=False: Changes are not permanent until we explicitly call db.commit()
# autoflush=False: Prevents premature writes before we are ready
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative Base Class
# All table models in app/models will inherit from this Base
Base = declarative_base()


# 5. FastAPI Dependency to safely acquire and release DB sessions
def get_db():
    """
    Generator that creates a new database session for an HTTP request
    and guarantees it is closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
