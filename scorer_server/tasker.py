from collections import namedtuple
from multiprocessing import Process, Queue
from scorer import Scorer
import queue
import time

from config import SCORER_COUNT


class Task:
    def __init__(self, name: str):
        self.name = name


class Attack(Task):
    pass


class Team(Task):
    pass


ScoreTask = namedtuple("ScoreTask", ['team', 'attack'])


class Tasker(Process):
    TIMEOUT = .25  # in seconds
    WORKER_COUNT = SCORER_COUNT  # number of processing to use to score.

    def __init__(self, queue: Queue, attacks=None):
        self.in_queue = queue
        self.out_queue = Queue(self.WORKER_COUNT*4)  # make sure queue is large enough to store the tasks.
        self.tasks = set()
        self.teams = set()
        self.attacks = set(attacks)
        self.scorers = set()
        super().__init__()

    def start_scorers(self):
        self.scorers = set()
        # setup and start scorer process pool.
        for _ in range(self.WORKER_COUNT):
            worker = Scorer(self.out_queue)
            worker.start()
            self.scorers.add(worker)

    def run(self):
        print("Starting Tasker...")
        self.start_scorers()
        try:
            while 1:
                sleep_needed = True
                # Get a task and update the task set.
                try:
                    task = self.in_queue.get(block=False, timeout=self.TIMEOUT)
                    if task is None:
                        break
                    if isinstance(task, Attack):
                        attack = task.name
                        if attack not in self.attacks:
                            self.attacks.add(attack)
                        for team in self.teams:
                            self.tasks.add(ScoreTask(team=team, attack=attack))
                    elif isinstance(task, Team):
                        team = task.name
                        if team not in self.teams:
                            self.teams.add(team)
                        for attack in self.attacks:
                            self.tasks.add(ScoreTask(team=team, attack=attack))
                    sleep_needed = False
                except queue.Empty:
                    pass

                # Update queue.
                for _ in range(self.WORKER_COUNT - self.out_queue.qsize()):
                    try:
                        task = self.tasks.pop()
                        print("Tasker: adding {} to scoring queue...".format(task))
                        self.out_queue.put(task)
                        sleep_needed = False
                    except KeyError:
                        pass  # No tasks avaible

                if sleep_needed:
                    time.sleep(self.TIMEOUT)
        except KeyboardInterrupt:
            pass

        # Kill scorers.
        for _ in range(self.WORKER_COUNT):
            self.out_queue.put(None)

        print("Tasker Process dying...")

