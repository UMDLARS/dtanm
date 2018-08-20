import logging
import sys

from scorer.manager import TeamManager, AttackManager
from scorer.worker import Scorer, ScoringConfig

sys.path.append('instance')

import config

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scorer_config = ScoringConfig(config.SCORING_BIN_NAME,
                                  config.SCORING_GOLD_NAME,
                                  config.SCORING_GOLD_SRC,
                                  config.RESULTS_DIR)
    team_manager = TeamManager(config.TEAM_DIR)
    attack_manager = AttackManager(config.UPLOAD_DIR, config.ATTACKS_DIR)

    s = Scorer(scorer_config, team_manager=team_manager, attack_manager=attack_manager)
    s.start()
    s.join()

