import pytest

from bot.services import query_controller as db_sess

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope = "function")
def controller(session):
    return db_sess.QueryController(session)


@pytest.fixture(scope = "function")
def controller_type(session, model):
    return db_sess.QueryController(session, model)


@pytest.fixture(scope = "function")
def controller_init(session, model):
    return db_sess.QueryController(session, model())


@pytest.fixture(scope = "function")
def controller_call_type(controller, model):
    return controller(model)


@pytest.fixture(scope = "function")
def controller_call_init(controller, model):
    return controller(model())


async def test_count_models(controller_type, controller_init, controller_call_type, controller_call_init, session, model):
    assert \
        await controller_type.count_models() == \
        await controller_init.count_models() == \
        await controller_call_init.count_models() == \
        await controller_call_type.count_models() == \
        await db_sess.count_models(session, model) == 0


async def test_get_models(controller_type, controller_init, controller_call_type, controller_call_init, session, model):
    assert \
        await controller_type.get_models() == \
        await controller_init.get_models() == \
        await controller_call_init.get_models() == \
        await controller_call_type.get_models() == \
        await db_sess.get_models(session, model)


async def test_get_model(controller_type, controller_init, controller_call_type, controller_call_init, session, model):
    assert \
        await controller_type.get_model(0) == \
        await controller_init.get_model(0) == \
        await controller_call_init.get_model(0) == \
        await controller_call_type.get_model(0) == \
        await db_sess.get_model(session, model, 0)


async def test_add_delete_model(controller_type, controller_init, controller_call_type, controller_call_init, session, model):
    add_model = model()

    assert await controller_type(add_model).add_model() == add_model
    assert await controller_init.add_model() != add_model
    assert await controller_call_init.add_model() != add_model
    assert await controller_call_type(add_model).add_model() == add_model
    assert await db_sess.add_model(session, add_model) == add_model

    assert \
        await controller_type.get_model(add_model.id) == \
        await controller_init.get_model(add_model.id) == \
        await controller_call_init.get_model(add_model.id) == \
        await controller_call_type.get_model(add_model.id) == \
        await db_sess.get_model(session, model, add_model.id)

    assert await controller_type(add_model).delete_model() == add_model
    assert await controller_init.delete_model() != add_model
    assert await controller_call_init.delete_model() != add_model
    assert await controller_call_type(add_model).delete_model() == add_model
    assert await db_sess.delete_model(session, add_model) == add_model

    assert \
        await controller_type.get_models() == \
        await controller_init.get_models() == \
        await controller_call_init.get_models() == \
        await controller_call_type.get_models() == \
        await db_sess.get_models(session, model)


async def test_update_model(controller_type, controller_init, controller_call_type, controller_call_init, session, model):
    add_model = model()

    assert await db_sess.add_model(session, add_model) == add_model

    await controller_type(add_model).update_model_values({'data': '1'})
    assert add_model.data == '1'

    await controller_init(add_model).update_model_values({'data': '2'})
    assert add_model.data == '2'

    await controller_call_init(add_model).update_model_values({'data': '3'})
    assert add_model.data == '3'

    await controller_call_type(add_model).update_model_values({'data': '4'})
    assert add_model.data == '4'
