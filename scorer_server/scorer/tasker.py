import queue
import time
from collections import deque
from logging import Logger
from multiprocessing import Process, Queue, Event
from typing import Set

from flask import g, current_app

from scorer.attack import Attack
from scorer.manager import AttackManager
from scorer.tasks import AttackUpdate, TeamUpdate, ScoreTask
from scorer.team import Team
from scorer.worker import Scorer, ScoringConfig


def get_attack_manager():
    if 'attack_manager' not in g:
        g.attack_manager = AttackManager(upload_dir=current_app.config["UPLOAD_DIR"],
                                         attacks_dir=current_app.config["ATTACKS_DIR"])

    return g.attack_manager


def get_task_queue():
    if 'task_queue' not in g:
        g.task_queue = Queue()
        # # Since we haven't created a queue.
        # # We know the tasker isn't started
        # get_tasker()

    return g.task_queue


def get_tasker():
    if 'tasker' not in g:
        current_app.logger.info("Creating Tasker...")
        g.tasker = Tasker(queue=get_task_queue(),
                          attacks=get_attack_manager().load_existing_attacks())

    return g.tasker


def start_tasker():
    get_tasker().start()


def stop_tasker(e=None):
    tasker = g.pop('tasker', None)
    if tasker:
        tasker.shutdown_flag.set()
        tasker.join()


def init_app(app):
    app.logger.info(f"Setting up tasker...")
    with app.app_context():
        start_tasker()
    app.teardown_appcontext(stop_tasker)


class Tasker(Process):
    teams: Set[Team]
    attacks: Set[Attack]
    shutdown_flag: Event  # If this is set: the Process will shutdown nicely.

    logger: Logger

    def __init__(self, queue: Queue, attacks=None):
        self.timeout = current_app.config["TASKER_LOOP_TIMEOUT_SEC"]
        self.worker_count = current_app.config["WORKER_COUNT"]  # number of processing to use to score.

        if attacks is None:
            self.attacks = set()
        else:
            self.attacks = set(attacks)

        self.in_queue = queue
        self.out_queue = Queue(self.worker_count)
        self.tasks = deque()  # a buffer of pending tasks for when the out_queue is full.
        self.teams = set()
        self.scorers = set()

        self.shutdown_flag = Event()
        self.logger = current_app.logger

        super().__init__()

    def start_scorers(self):
        self.scorers = set()
        # setup and start scorer process pool.
        for _ in range(self.worker_count):
            scorer_config = ScoringConfig(current_app.config["SCORING_BIN_NAME"],
                                          current_app.config["SCORING_GOLD_NAME"],
                                          current_app.config["SCORING_GOLD_SRC"])
            worker = Scorer(self.out_queue, scorer_config)
            worker.start()
            self.scorers.add(worker)

    def process_in_queue(self):
        """

        Returns: True if a task was processed.
        """
        try:
            task = self.in_queue.get(block=False, timeout=.01)
            if task is None:
                raise InterruptedError
            if isinstance(task, AttackUpdate):
                attack = task.data
                if attack not in self.attacks:
                    self.attacks.add(attack)
                for team in self.teams:
                    task = ScoreTask(team=team, attack=attack)
                    if task not in self.tasks:
                        self.tasks.append(task)
            elif isinstance(task, TeamUpdate):
                team = task.data
                if team not in self.teams:
                    self.teams.add(team)
                for attack in self.attacks:
                    task = ScoreTask(team=team, attack=attack)
                    if task not in self.tasks:
                        self.tasks.append(task)
            return True
        except queue.Empty:
            return False

    def update_out_queue(self):
        """

        Returns: True if a task was processed.
        """
        task_processed = False
        while self.worker_count - self.out_queue.qsize() and len(self.tasks):
            task = self.tasks.popleft()
            self.logger.debug("Tasker: adding {} to scoring queue...".format(task))
            self.out_queue.put(task)
            task_processed = True
        return task_processed

    def run(self):
        self.logger.info("Starting Tasker...")
        self.start_scorers()
        try:
            while not self.shutdown_flag.is_set():
                sleep_needed = True

                # Get a task and update the task set.
                # If we got one we need not sleep.
                if self.process_in_queue():
                    sleep_needed = False

                # Update task queue from task set.
                # If we got one we need not sleep.
                if self.update_out_queue():
                    sleep_needed = False

                if sleep_needed:
                    time.sleep(self.timeout)
        except InterruptedError:
            pass
        except KeyboardInterrupt:
            pass

        self.logger.info("Tasker Process shutting down...")

        # Shutdown workers.
        for _ in range(self.worker_count):
            self.out_queue.put(None)
