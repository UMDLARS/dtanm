import time
from dataclasses import dataclass
from typing import Callable

import pytest
import requests


@dataclass
class Config:
    url: str


@pytest.fixture
def local_server():
    # TODO: Rewrite this using docker compose to start server.
    print("Make sure local server is running...")
    config = Config(url="http://localhost:3001")
    yield config


def get_results(base_url):
    return requests.get(f'{base_url}/results').json()


def wait_till(func: Callable[[], bool], timeout_sec):
    start_time = time.time()
    while not func():
        assert time.time() - start_time < timeout_sec, "Timed out"
        time.sleep(1)


@pytest.mark.end_to_end
def test_end_to_end_1(local_server):
    baseurl = local_server.url

    HASHES = {
        "9314153eec32c69e5891e30455b175e701fadf42596586df1ef188b4cff1f21fb1b67a7110188ddc0f4d0ab10833bb5d567881fda43965c7b98b715726fe6df9": "attack_hello",
        "b5a6c5463da84a1e69ddf2cc01647d1cd422dd82abd5024cc5887ed3f2694882cb0882c37c99f7db1560789648ed9040bda830945e38b5a1b700fc8184a196dd": "attack_hi",
        "9926f3d3addc136e0b4e6bbd4ec1c38b579d6d958abd7559f746f9d93161d58d514b03e229ecfb2434a764a4106f13e7508a08660a7b23c5e5acb015337b23ed": "attack_blank",
    }
    EXPECTED_RESULTS = {
        ("team1", "69861e5eebf483000b932f1246d4b99c4fa1298e", "attack_hi"): True,
        ("team1", "69861e5eebf483000b932f1246d4b99c4fa1298e", "attack_hello"): False,
        ("team1", "69861e5eebf483000b932f1246d4b99c4fa1298e", "attack_blank"): False,

        ("team2", "40557e80d37291796403232ddb3fd0d0d3841b51", "attack_hi"): True,
        ("team2", "40557e80d37291796403232ddb3fd0d0d3841b51", "attack_hello"): True,
        ("team2", "40557e80d37291796403232ddb3fd0d0d3841b51", "attack_blank"): False,

        ("team3", "870fcfbeb12742150f099bec5ece0789ee8a4cff", "attack_hi"): True,
        ("team3", "870fcfbeb12742150f099bec5ece0789ee8a4cff", "attack_hello"): True,
        ("team3", "870fcfbeb12742150f099bec5ece0789ee8a4cff", "attack_blank"): True,
    }
    TIMEOUT_SEC = 10

    def ping():
        try:
            requests.get(f'{baseurl}')
            return True
        except requests.ConnectionError:
            return False

    wait_till(ping, timeout_sec=TIMEOUT_SEC)

    assert requests.get(f"{baseurl}/attack/attack_blank.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/attack/attack_hi.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/attack/attack_hello.tar.gz").status_code == 200
    assert requests.get(f"{baseurl}/team/team1").status_code == 200
    assert requests.get(f"{baseurl}/team/team2").status_code == 200
    assert requests.get(f"{baseurl}/team/team3").status_code == 200

    wait_till(lambda: len(get_results(baseurl)) >= len(EXPECTED_RESULTS), timeout_sec=TIMEOUT_SEC)

    assert len(get_results(baseurl)) == len(EXPECTED_RESULTS)

    results = {}
    for res in get_results(baseurl):
        results[(res['team'], res['commit'], HASHES[res['attack']])] = res['passed']

    assert len(results) == len(EXPECTED_RESULTS)
    assert results.keys() == EXPECTED_RESULTS.keys()

    for key, excepted_res in EXPECTED_RESULTS.items():
        assert results[key] == excepted_res
