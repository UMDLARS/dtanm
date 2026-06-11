from __future__ import annotations
from web import db
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from web.models.team import Team
    from web.models.attack import Attack

class Result(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    attack_id: Mapped[int] = mapped_column(ForeignKey('attack.id'))
    attack: Mapped["Attack"] = relationship(back_populates='results')

    # Result is either from `gold` or from a team
    gold: Mapped[bool] = mapped_column()
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey('team.id'))
    team: Mapped[Optional["Team"]] = relationship(back_populates="results")

    commit_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    passed: Mapped[Optional[bool]] = mapped_column()

    # psycopg2 returns memoryview objects, unless it's zero length, in which
    # case it returns b'', of type bytes. To keep this consistent, we explicitly
    # cast to bytes here.
    _stdout: Mapped[bytes] = mapped_column("stdout")
    @property
    def stdout(self):
        return bytes(self._stdout)
    #stdout_hash: Mapped[str] = mapped_column(String(64)) # Unused
    stdout_correct: Mapped[Optional[bool]] = mapped_column()

    _stderr: Mapped[bytes] = mapped_column("stderr")
    @property
    def stderr(self):
        return bytes(self._stderr)
    #stderr_hash: Mapped[str] = mapped_column(String(64)) # Unused
    stderr_correct: Mapped[Optional[bool]] = mapped_column()

    #filesystem_hash: Mapped[str] = mapped_column(String(64)) # TODO
    #filesystem_correct: Mapped[bool] = mapped_column()

    return_code: Mapped[int] = mapped_column()
    return_code_correct: Mapped[Optional[bool]] = mapped_column()

    seconds_to_complete: Mapped[float] = mapped_column()

    # Contains custom output, such as compilation errors
    output: Mapped[Optional[str]] = mapped_column(Text())

    @property
    def correct_result(self) -> Result:
        return self.attack.gold_result
