import pytest
import os
import requests
import re

from requests.exceptions import ConnectionError
@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Get an absolute path to the  `docker-compose.yml` file."""
    return os.path.join(str(pytestconfig.rootdir), "docker-compose.yml")

def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def http_service(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("web", 5000)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.5, check=lambda: is_responsive(url)
    )
    return url


@pytest.fixture(scope="session")
def admin_user(http_service) -> requests.Session:
    return get_session_for_user(http_service, "swift106@d.umn.edu", "password")

def get_session_for_user(http_service, user, password) -> requests.Session:
    s = requests.Session()

    # get the csrf_token
    res = s.get(f"{http_service}/login")
    # eh https://stackoverflow.com/a/1732454/3814663
    pattern = re.compile('<input id="csrf_token" name="csrf_token" type="hidden" value="(.*?)">')
    match = pattern.search(res.text)
    csrf_token = match.group(1)

    # make the login request (adds cookie to session)
    s.post(f"{http_service}/login",
        data={
            "email": user,
            "password": password,
            "csrf_token": csrf_token,
        })

    res = s.get(f"{http_service}/change") # any logged in user can access the change password page
    assert f"{user} |" in res.text
    return s

@pytest.fixture(scope="session")
def user(http_service, admin_user) -> requests.Session:
    try:
        return get_session_for_user(http_service, "test_user@chandlerswift.com", "password")
    except AssertionError:
        # else, user doesn't exist, let's create it
        # Ensure we have at least one team
        admin_user.post(f"{http_service}/admin/add_team", data={
            "name": "New Team",
        }, headers={
            'referer': f"{http_service}/admin/teams"
        })
        # and put a user in it
        admin_user.post(f"{http_service}/admin/add_user", data={
            "name": "Test User",
            "email": "test_user@chandlerswift.com",
            "password": "password",
            "teamid": 1,
        }, headers={
            'referer': f"{http_service}/admin/users"
        })

    return get_session_for_user(http_service, "test_user@chandlerswift.com", "password")
