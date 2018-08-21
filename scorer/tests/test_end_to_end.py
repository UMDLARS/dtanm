import json
import os
import shutil
import time

import pytest
import requests
from pytest_localserver.http import WSGIServer

from scorer import create_app
from tests import get_test_resource


# @contextmanager
# def environ(**vars):
#     yield
#     for arg in vars:
#         os.environ.unsetenv(arg)
#     for arg, value in env_data:
#         os.environ[arg] = value


# def with_environ(**vars):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kargs):
#             return_value = func(*args, **kargs)
#             return return_value
#
#         return wrapper
#
#     return decorator


@pytest.fixture
def temp_root_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield os.path.join(dir_name, 'root')
    shutil.rmtree(dir_name)


@pytest.fixture
def local_server(temp_root_dir):
    shutil.copytree(get_test_resource('mock_root'), temp_root_dir)
    config = {
        'UPLOAD_DIR': os.path.join(temp_root_dir, 'cctf/server/uploads'),
        'ATTACKS_DIR': os.path.join(temp_root_dir, 'cctf/attacks'),
        'TEAM_DIR': os.path.join(temp_root_dir, 'cctf/server/gitrepos'),
        'RESULTS_DIR': os.path.join(temp_root_dir, 'cctf/results'),
        'SCORING_BIN_NAME': 'echo',
        'SCORING_GOLD_NAME': 'gold',
        'SCORING_GOLD_SRC': os.path.join(temp_root_dir, 'cctf/gold'),
        'TASKER_LOOP_TIMEOUT_SEC': 0.1,
        'WORKER_COUNT': 1,
        'START_TASKER': True,
        'DEBUG': True,
        'TESTING': True
    }

    env_data = os.environ.copy()
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'

    app = create_app(config)
    server = WSGIServer(application=app)
    server.start()
    requests.get(f"{server.url}")
    server.res_dir = os.path.join(temp_root_dir, 'cctf/results')
    # yield Mock()
    yield server
    server.stop()
    os.environ.unsetenv('WERKZEUG_RUN_MAIN')
    for arg, value in env_data.items():
        os.environ[arg] = value


# Rewrite this using docker compose.
@pytest.mark.end_to_end
def test_end_to_end_1(local_server):
    baseurl = local_server.url
    assert requests.get(f"{baseurl}/attack/attack_blank.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/attack/attack_hi.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/attack/attack_hello.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/team/team1").status_code == 200
    assert requests.get(f"{baseurl}/team/team2").status_code == 200
    assert requests.get(f"{baseurl}/team/team3").status_code == 200

    hashes = {
        "9314153eec32c69e5891e30455b175e701fadf42596586df1ef188b4cff1f21fb1b67a7110188ddc0f4d0ab10833bb5d567881fda43965c7b98b715726fe6df9": "attack_hello",
        "b5a6c5463da84a1e69ddf2cc01647d1cd422dd82abd5024cc5887ed3f2694882cb0882c37c99f7db1560789648ed9040bda830945e38b5a1b700fc8184a196dd": "attack_hi",
        "9926f3d3addc136e0b4e6bbd4ec1c38b579d6d958abd7559f746f9d93161d58d514b03e229ecfb2434a764a4106f13e7508a08660a7b23c5e5acb015337b23ed": "attack_blank",
        }

    TIMEOUT_SEC = 10

    start_time = time.time()
    while len(os.listdir(local_server.res_dir)) < 3 * 3:
        assert time.time() - start_time < TIMEOUT_SEC, "Timed out"
        time.sleep(1)

    assert len(os.listdir(local_server.res_dir)) == 3 * 3

    results = {}

    for file_name in os.listdir(local_server.res_dir):
        team, attack_hash = file_name.replace(".json", "").split("_")
        with open(local_server.res_dir + "/" + file_name) as fp:
            results[(team, hashes[attack_hash])] = json.load(fp)

    assert results[("team1", "attack_hi")]['passed']
    assert results[("team1", "attack_hi")]['commit'] == '69861e5eebf483000b932f1246d4b99c4fa1298e'
    assert not results[("team1", "attack_hello")]['passed']
    assert results[("team1", "attack_hello")]['commit'] == '69861e5eebf483000b932f1246d4b99c4fa1298e'
    assert not results[("team1", "attack_blank")]['passed']
    assert results[("team1", "attack_blank")]['commit'] == '69861e5eebf483000b932f1246d4b99c4fa1298e'

    assert results[("team2", "attack_hi")]['passed']
    assert results[("team2", "attack_hi")]['commit'] == '40557e80d37291796403232ddb3fd0d0d3841b51'
    assert results[("team2", "attack_hello")]['passed']
    assert results[("team2", "attack_hello")]['commit'] == '40557e80d37291796403232ddb3fd0d0d3841b51'
    assert not results[("team2", "attack_blank")]['passed']
    assert results[("team2", "attack_blank")]['commit'] == '40557e80d37291796403232ddb3fd0d0d3841b51'

    assert results[("team3", "attack_hi")]['passed']
    assert results[("team3", "attack_hi")]['commit'] == '870fcfbeb12742150f099bec5ece0789ee8a4cff'
    assert results[("team3", "attack_hello")]['passed']
    assert results[("team3", "attack_hello")]['commit'] == '870fcfbeb12742150f099bec5ece0789ee8a4cff'
    assert results[("team3", "attack_blank")]['passed']
    assert results[("team3", "attack_blank")]['commit'] == '870fcfbeb12742150f099bec5ece0789ee8a4cff'
