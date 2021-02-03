import requests
import pytest
from conftest import get_session_for_user
import re

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

def test_change_user_password(http_service, admin_user):
    # since we'll be changing the password, create a new user. Don't want to
    # mess up the user fixture's user for other tests...
    admin_user.post(f"{http_service}/admin/add_user", data={
        "name": "chpasswd user",
        "email": "chpasswd_user@chandlerswift.com" ,
        "password": "old_password",
        "teamid": "",
    })
    s = get_session_for_user(http_service, "chpasswd_user@chandlerswift.com", "old_password")
    assert s

    # get the csrf_token
    res = s.get(f"{http_service}/change")
    # eh https://stackoverflow.com/a/1732454/3814663
    pattern = re.compile('<input id="csrf_token" name="csrf_token" type="hidden" value="(.*?)">')
    match = pattern.search(res.text)
    csrf_token = match.group(1)

    response = s.post(f"{http_service}/change", data={
        "csrf_token": csrf_token,
        "password": "old_password",
        "new_password": "new_password",
        "new_password_confirm": "new_password",
    })

    with pytest.raises(AssertionError): # verify user no longer has old login
        get_session_for_user(http_service, "chpasswd_user@chandlerswift.com", "old_password")

    assert get_session_for_user(http_service, "chpasswd_user@chandlerswift.com", "new_password")
