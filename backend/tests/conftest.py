import os
import sys
import importlib

import pytest
from flask_jwt_extended import create_access_token


@pytest.fixture
def app_module(monkeypatch):
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    import db

    monkeypatch.setattr(db, "connect_databases", lambda: None)

    if "app" in sys.modules:
        app_module = importlib.reload(sys.modules["app"])
    else:
        app_module = importlib.import_module("app")

    app_module.app.config["TESTING"] = True
    return app_module


@pytest.fixture
def app_client(app_module):
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers(app_module):
    with app_module.app.app_context():
        token = create_access_token(identity="user_1")
    return {"Authorization": f"Bearer {token}"}

