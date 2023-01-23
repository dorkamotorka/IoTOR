#!/usr/bin/env python3

import pytest

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project import create_app
from flask.testing import FlaskClient


# re-usable fixtures

@pytest.fixture()
def app():
    yield create_app()

@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


# tests

def test_main_get_1(client):
    with client as c:
        response = c.get("/")
        assert response.status_code == 200
        assert "Get Weather" in response.text

def test_main_get_2(client):
    with client as c:
        response = c.get("/")
        assert response.status_code == 200
        assert not "Temperature" in response.text

def test_assets_200(client):
    with client as c:
        response = c.get("/assets/weather.jpg")
        assert response.status_code == 200
        assert response.content_length > 100_000

def test_assets_404(client):
    with client as c:
        response = c.get("/assets/does-not-exist")
        assert response.status_code == 404

def test_health(client):
    with client as c:
        response = c.get("/health")
        assert response.status_code == 200
