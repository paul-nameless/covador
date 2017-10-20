import pytest

import asyncio

from sanic import Sanic
from sanic import views
from sanic import response

from covador import opt
from covador.sanic import form
from covador.sanic import m_form
from covador.sanic import params
from covador.sanic import rparams
from covador.sanic import json_body
from covador.sanic import query_string
from covador.sanic import m_query_string

from . import helpers


@pytest.yield_fixture
def app():
    app = Sanic("test_sanic_app")

    @app.route("/query/string/", methods=['GET'])
    @query_string(a=int)
    @asyncio.coroutine
    def test_query_string(request, **kwargs):
        return response.json(kwargs)

    @app.route("/form/", methods=['POST'])
    @form(a=int)
    @asyncio.coroutine
    def test_form(request, **kwargs):
        return response.json(kwargs)

    @app.route("/json/body/", methods=['POST'])
    @json_body(a=opt(int))
    @asyncio.coroutine
    def test_json_body(request, **kwargs):
        return response.json(kwargs)

    @app.route("/params/", methods=['POST'])
    @params(a=int, b=int)
    @asyncio.coroutine
    def test_params(request, **kwargs):
        return response.json(kwargs)

    @app.route("/rparams/<a>/", methods=['POST'])
    @rparams(a=int)
    @asyncio.coroutine
    def test_rparams(request, **kwargs):
        return response.json(kwargs)

    class SimpleView(views.HTTPMethodView):
        @m_query_string(a=int)
        @asyncio.coroutine
        def get(self, request, **kwargs):
            return response.json(kwargs)

        @m_form(a=int)
        @asyncio.coroutine
        def post(self, request, **kwargs):
            return response.json(kwargs)

    app.add_route(SimpleView.as_view(), '/cbv/')
    yield app


@pytest.fixture
def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


@asyncio.coroutine
def test_query_string(test_cli):
    resp = yield from test_cli.get('/query/string/', params={'a': 2})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}

    resp = yield from test_cli.get('/cbv/', params={'a': 2})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}


@asyncio.coroutine
def test_query_string_error(test_cli):
    resp = yield from test_cli.get('/query/string/')
    assert resp.status == 400
    resp_json = yield from resp.json()
    assert resp_json == {'details': {'a': 'Required item'}, 'error': 'bad-request'}


@asyncio.coroutine
def test_form(test_cli):
    resp = yield from test_cli.post('/form/', data={'a': 2})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}

    body, mct = helpers.encode_multipart([('a', '2')])
    resp = yield from test_cli.post('/form/', data=body,
                                    headers={'Content-Type': mct})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}

    resp = yield from test_cli.post('/cbv/', data={'a': 2})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}


@asyncio.coroutine
def test_json_body(test_cli):
    resp = yield from test_cli.post('/json/body/', json={'a': 2})
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}

    resp = yield from test_cli.post('/json/body/', data=b'')
    resp_json = yield from resp.json()
    assert resp_json == {'a': None}


@asyncio.coroutine
def test_params(test_cli):
    resp = yield from test_cli.post('/rparams/2/')
    assert resp.status == 200
    resp_json = yield from resp.json()
    assert resp_json == {'a': 2}
