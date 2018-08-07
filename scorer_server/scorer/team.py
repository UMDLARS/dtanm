class Team:
    def __init__(self, name):
        self.name = name

    def get_git_remote(self):
        return f"/cctf/gitrepos/{self.name}"

    def __eq__(self, other):
        return isinstance(other, Team) and other.name == self.name

    def __hash__(self):
        return hash(self.name)
