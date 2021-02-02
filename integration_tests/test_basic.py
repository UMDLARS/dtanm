import requests


def test_status_code(http_service):
    response = requests.get(http_service)

    assert response.status_code == 200
