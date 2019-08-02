import pytest
from flask import url_for
from mock import patch

from scorer import create_app
from scorer.attack import Attack
from scorer.team import Team


@pytest.fixture
def app():
    app = create_app({'DEBUG': True, 'TESTING': True})
    return app


@patch('scorer.api.get_team_manager')
@patch('scorer.api.add_team')
def test_simple_team_update(add_team, mocked_get_team_manager, client):
    team_id = "Some Team"
    process_team = mocked_get_team_manager.return_value.process_team
    process_team.return_value = Team(team_id)

    res = client.get(url_for('api.team_update', team_name="123"))

    assert res.status_code == 200
    assert 'id' in res.json and res.json['id'] == team_id
    process_team.assert_called_with("123")
    add_team.assert_called_with(team_id)


@patch('scorer.api.get_attack_manager')
@patch('scorer.api.add_attack')
def test_simple_new_attack(add_attack, mocked_get_attack_manager, client):
    attack_id = "Some Attack"
    process_attack = mocked_get_attack_manager.return_value.process_attack
    process_attack.return_value = Attack(attack_id)

    res = client.get(url_for('api.new_attack', attack_name="123"))

    assert res.status_code == 200
    assert 'id' in res.json and res.json['id'] == attack_id
    process_attack.assert_called_with("123")
    add_attack.assert_called_with(attack_id)
