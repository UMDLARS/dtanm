from pathlib import PosixPath
from typing import List


def parse_args(stream: bytes) -> List[bytes]:
    # This is an attempt to parse the argument string using regex.
    # matches = re.findall(r'(["\'][-\w\s]*["\']|([\w-]*(\\ )*[\w-]*)*)', attack)
    # Remove all blanks
    # args = map(lambda x: x[0], filter(lambda x: x[0], matches))
    # return args

    # TODO(derpferd): make single quotes and backslashes work.
    args = stream.split()  # Split on the spaces

    # put quotes that were split back together
    i = 0
    in_quote = False
    while i < len(args):
        if in_quote:
            args[i - 1] += b" " + args.pop(i)
            i -= 1
        if args[i].count(b'"') % 2 == 1:
            in_quote = True
        else:
            in_quote = False
        i += 1

    for i in range(len(args)):
        args[i] = args[i].replace(b'"', b"")

    return args


class Attack(PosixPath):
    @property
    def stdin_filepath(self) -> str:
        return str(self.joinpath("stdin"))

    @property
    def cmd_args(self) -> List:
        with open(str(self.joinpath("cmd_args")), "rb") as fp:
            return parse_args(fp.read())

    @property
    def env(self) -> str:
        return str(self.joinpath("env"))

    def __repr__(self):
        return f"<Attack @ '{self.resolve()}'>"
