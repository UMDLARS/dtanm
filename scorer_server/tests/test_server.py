import pytest
from flask import url_for
from mock import patch

from scorer import create_app
from scorer.attack import Attack
from scorer.tasks import TeamUpdate, AttackUpdate
from scorer.team import Team


@pytest.fixture
def app():
    app = create_app({'DEBUG': True, 'TESTING': True})
    return app


@patch('scorer.api.get_team_manager')
@patch('scorer.api.add_team')
def test_simple_team_update(add_team, mocked_get_team_manager, client):
    process_team = mocked_get_team_manager.return_value.process_team
    process_team.return_value = Team("Some Team")

    assert client.get(url_for('api.team_update', team_name="123")).status_code == 200
    add_team.assert_called_with("Some Team")


@patch('scorer.api.get_attack_manager')
@patch('scorer.api.add_attack')
def test_simple_new_attack(add_attack, mocked_get_attack_manager, client):
    process_attack = mocked_get_attack_manager.return_value.process_attack
    process_attack.return_value = Attack("Some Attack")

    assert client.get(url_for('api.new_attack', attack_name="123")).status_code == 200

    process_attack.assert_called_with("123")
    add_attack.assert_called_with("Some Attack")
