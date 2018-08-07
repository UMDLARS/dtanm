import pytest

from scorer import create_app


@pytest.fixture
def app():
    app = create_app()
    return app
