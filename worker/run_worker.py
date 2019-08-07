import logging
import sys
from redis import Redis
import os

from worker import Scorer, ScoringConfig

sys.path.append('/pack')
import config

if __name__ == '__main__':
    redis =  Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                   port=os.environ.get('REDIS_PORT', 6379),
                   db=os.environ.get('REDIS_DB', 0))
    logging.basicConfig(level=logging.INFO)

    scorer_config = ScoringConfig(config.SCORING_BIN_NAME, config.SCORING_GOLD_NAME, "/pack/gold")

    s = Scorer(scorer_config, redis)
    s.start()
    s.join()
