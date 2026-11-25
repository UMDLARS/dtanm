from pathlib import PosixPath
from typing import List

class Attack(PosixPath):
    @property
    def stdin_filepath(self) -> str:
        return str(self.joinpath("stdin"))

    @property
    def cmd_args(self) -> List:
        try:
            with open(str(self.joinpath("cmd_args")), "rb") as fp:
                return fp.read()
        except:
            return b''

    @property
    def env(self) -> str:
        return str(self.joinpath("env"))

    @property
    def envs(self):
        try:
            with open(self.env) as f:
                return [line.rstrip() for line in f.readlines()]
        except:
            return []

    @property
    def files(self) -> str:
        return str(self.joinpath("files"))

    @property
    def id(self) -> str:
        return self.name

    def __repr__(self):
        return f"<Attack @ '{self.resolve()}'>"
