import logging
import sys
from redis import Redis
import os

from worker import Scorer, ScoringConfig

sys.path.append('instance')
import config

if __name__ == '__main__':
    redis =  Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                   port=os.environ.get('REDIS_PORT', 6379),
                   db=os.environ.get('REDIS_DB', 0))
    logging.basicConfig(level=logging.INFO)

    scorer_config = ScoringConfig("echo", "gold", "/pack/gold")

    #scorer_config = ScoringConfig(config.SCORING_BIN_NAME,
    #                              config.SCORING_GOLD_NAME,
    #                              config.SCORING_GOLD_SRC,
    #                              config.RESULTS_DIR)
    #team_manager = TeamManager(config.TEAM_DIR)
    #attack_manager = AttackManager(config.UPLOAD_DIR, config.ATTACKS_DIR)

    s = Scorer(scorer_config, redis)
    s.start()
    s.join()
