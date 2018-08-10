import pytest
from flask import url_for
from mock import patch

from scorer import create_app
from scorer.tasks import TeamUpdate, AttackUpdate


@pytest.fixture
def app():
    app = create_app({'DEBUG': True, 'TESTING': True})
    return app


@patch('scorer.api.get_team_manager')
@patch('scorer.api.get_task_queue')
def test_simple_team_update(mocked_get_task_queue, mocked_get_team_manager, client):
    queue = mocked_get_task_queue.return_value
    process_team = mocked_get_team_manager.return_value.process_team
    process_team.return_value = "Some Team"

    assert client.get(url_for('api.team_update', team_name="123")).status_code == 200
    queue.put.assert_called_with(TeamUpdate("Some Team"))


@patch('scorer.api.get_attack_manager')
@patch('scorer.api.get_task_queue')
def test_simple_new_attack(mocked_get_task_queue, mocked_get_attack_manager, client):
    queue = mocked_get_task_queue.return_value
    process_attack = mocked_get_attack_manager.return_value.process_attack
    process_attack.return_value = "Some Attack"

    assert client.get(url_for('api.new_attack', attack_name="123")).status_code == 200

    process_attack.assert_called_with("123")
    queue.put.assert_called_with(AttackUpdate("Some Attack"))
