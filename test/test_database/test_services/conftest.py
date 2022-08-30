import pytest


@pytest.fixture(scope = 'function')
def session_controller(db_sess, session):
    return db_sess.QueryController(session)
