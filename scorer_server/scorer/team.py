import os


class Team:
    def __init__(self, path):
        self.root, self.name = os.path.split(path)
        self.path = path

    def get_git_remote(self):
        return self.path

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Team {self.path}>"

    def __eq__(self, other):
        return isinstance(other, Team) and other.path == self.path

    def __hash__(self):
        return hash(self.path)
