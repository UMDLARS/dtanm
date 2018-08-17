import logging
from scorer.tasker import Tasker

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    t = Tasker()
    t.start()
    t.join()

