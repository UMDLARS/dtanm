from logging import Logger

from mock import patch, Mock

from scorer.attack import Attack
from scorer.tasks import ScoreTask
from scorer.team import Team
from scorer.worker import Scorer, ScoringConfig
from tests import get_test_resource


@patch('scorer.worker.Gold')
@patch('scorer.worker.Exerciser')
@patch('scorer.worker.are_dirs_same')
@patch('scorer.worker.current_app')
def test_score(mock_app, mock_are_dirs_same, mock_exerciser, mock_gold):
    mock_app.logger = Logger(__name__)
    mock_are_dirs_same.return_value = True
    mock_exerciser.return_value.__enter__.return_value = Mock()
    mock_gold.return_value.__enter__.return_value = Mock()

    config = ScoringConfig('echo', 'echo', get_test_resource('echo'), None)
    scorer = Scorer(None, config)

    task = ScoreTask(team=Team('Team1'), attack=Attack('attack1'))
    scorer.score(task)
