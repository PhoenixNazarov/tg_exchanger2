import pytest

pytestmark = pytest.mark.asyncio


async def test_empty(db_sess, session, model):
    assert await db_sess.count_models(session, model) == 0
    assert await db_sess.get_models(session, model) == []
    assert await db_sess.get_model(session, model, 0) is None


async def test_add_model(session, model, db_sess):
    model1 = model()
    model2 = await db_sess.add_model(session, model1)
    assert model1 == model2
    assert await db_sess.count_models(session, model) == 1
    assert await db_sess.get_model(session, model, model1.id) == model2
    assert await db_sess.get_models(session, model) == [model1]


async def test_add_get(session, model, db_sess):
    add_model1 = await db_sess.add_model(session, model())
    get_model1 = await db_sess.get_model(session, model, add_model1.id)
    assert get_model1 == add_model1
    assert await db_sess.count_models(session, model) == 1
    assert await db_sess.get_models(session, model) == [add_model1]

    add_model2 = await db_sess.add_model(session, model())
    get_model2 = await db_sess.get_model(session, model, add_model2.id)
    assert add_model2 == get_model2
    assert add_model1 != add_model2
    assert get_model1 != get_model2
    assert await db_sess.count_models(session, model) == 2
    assert await db_sess.get_models(session, model) == [add_model1, add_model2]


async def test_delete_model(session, model, db_sess):
    model1 = await db_sess.add_model(session, model())
    model2 = await db_sess.add_model(session, model())
    assert model1 != model2

    assert await db_sess.get_model(session, model, model1.id) == model1
    del_model = await db_sess.delete_model(session, model1)
    assert model1 == del_model
    assert await db_sess.get_model(session, model, del_model.id) is None
    assert await db_sess.get_model(session, model, model2.id) == model2


async def test_update_model(session, model, db_sess):
    model1 = await db_sess.add_model(session, model())
    data = '1'
    assert model1.data != data
    await db_sess.update_model_values(session, model1, {'data': data})
    assert model1.data == data


async def qtest_sessions(session_maker, model, db_sess):
    session1 = session_maker()
    session2 = session_maker()
    model1 = await db_sess.add_model(session1, model())
    model2 = await db_sess.add_model(session2, model())

    session3 = session_maker()
    assert await db_sess.count_models(session1, model) == 1
    assert await db_sess.count_models(session2, model) == 1
    assert await db_sess.count_models(session3, model) == 2

    assert await db_sess.get_model(session1, model, model1.id) == model1
    assert await db_sess.get_model(session2, model, model2.id) != model1

    ses3_models = [
        await db_sess.get_model(session3, model, model1.id),
        await db_sess.get_model(session3, model, model2.id)
    ]
    assert await db_sess.get_models(session3, model) == ses3_models

    assert model1 == ses3_models
    assert model2 == ses3_models


@pytest.mark.parametrize('w_session,w_model,w_id,w_data', [
    (None, 'session', 4, 'model'),
    ('model', 'model', 0, []),
    ('None', {}, None, 2),
    ('', 'session', 5, 5),
    (1, 1, 'session', None),
    ('session', None, 1, ''),
    ({}, None, 1, {}),
    ('session', [], 1, 'sessiom'),
    ('session', None, 'model', {}),  # todo
])
class TestExceptionArgs:
    async def test_count(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.count_models(w_session, w_model)

    async def test_add(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.add_model(w_session, w_model)

    async def test_get(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.get_model(w_session, w_model, w_id)

    async def test_gets(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.get_models(w_session, w_model)

    async def test_updates(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.update_model_values(w_session, w_model, w_data)

    async def test_delete(self, w_session, w_model, w_id, w_data, db_sess):
        with pytest.raises(Exception) as e_info:
            await db_sess.add_model(w_session, w_model)


async def test_exceptions2(session, model, db_sess):
    model1 = model()
    with pytest.raises(Exception) as e_info:
        await db_sess.update_model_values(session, model1, {'data': 1})
    await db_sess.add_model(session, model1)
    with pytest.raises(Exception) as e_info:
        await db_sess.update_model_values(session, model1, {'data': '1', 'asd': 4})
    await db_sess.update_model_values(session, model1, {'data': '1'})


async def test_exceptions3(session, model, db_sess):
    model1 = model()
    model2 = await db_sess.delete_model(session, await db_sess.add_model(session, model1))
    assert model1 == model2
    await db_sess.delete_model(session, model1)  # todo


async def test_query_controller(session, model, db_sess):
    mod = model()
    controller = db_sess.QueryController(session)
    controller_type = db_sess.QueryController(session, model)
    controller_init = db_sess.QueryController(session, mod)

    assert \
        await controller_type.count_models() == \
        await controller_init.count_models() == \
        await controller(model).count_models() == \
        await controller(mod).count_models() == \
        await db_sess.count_models(session, model) == 0


