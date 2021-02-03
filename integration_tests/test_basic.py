import requests


def test_load_home_page(http_service):
    response = requests.get(http_service)
    assert response.status_code == 200
    assert "Welcome to DTANM!" in response.content.decode()

def test_load_instructions(http_service):
    response = requests.get(f"{http_service}/instructions/")
    assert response.status_code == 200
    assert "The sloths and the eagles are at all-out war." in response.content.decode()

    response = requests.get(f"{http_service}/instructions/examples")
    assert response.status_code == 200
    assert "EXAMPLE TEST CASES" in response.content.decode()

def test_stats_ui(http_service):
    response = requests.get(f"{http_service}/stats")
    assert response.status_code == 200
    assert "Competition Statistics" in response.content.decode()

def test_stats_json(http_service):
    response = requests.get(f"{http_service}/stats.json")
    assert response.status_code == 200
    assert "Attacks submitted" in response.json()

def test_functional_scoring_worker(http_service):
    response = requests.get(f"{http_service}/stats.json")
    assert response.status_code == 200
    assert "Scoring workers" in response.json()
    assert response.json()["Scoring workers"] > 0

