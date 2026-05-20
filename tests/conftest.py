import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from main import create_app
from database.session import DATABASE_URL

# Ensure test DB is used
os.environ["TESTING"] = "1"

# ---------------------------------------------------
# Test engine (DO NOT use db.engine)
# ---------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# ---------------------------------------------------
# App fixture
# ---------------------------------------------------
@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


# ---------------------------------------------------
# DB session fixture (transactional isolation)
# ---------------------------------------------------
@pytest.fixture
def database_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ---------------------------------------------------
# Flask test client
# ---------------------------------------------------
@pytest.fixture
def client(app, database_session):
    import database.session as db_session_module

    # IMPORTANT: patch get_db safely
    db_session_module.get_db = lambda: database_session

    with app.app_context():
        with app.test_client() as client:
            yield client

@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield