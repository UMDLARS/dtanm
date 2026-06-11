from web import db
from flask_security import UserMixin, RoleMixin
from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from web.models.team import Team

#class RolesUsers(db.Model):
#    __tablename__ = 'roles_users'
#    id = mapped_column(db.Integer(), primary_key=True)
#    user_id = mapped_column('user_id', db.Integer(), db.ForeignKey('user.id'))
#    role_id = mapped_column('role_id', db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = 'role'
    id: Mapped[int] = mapped_column(primary_key=True)

class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)

    team_id: Mapped[Optional[int]] = mapped_column( db.ForeignKey('team.id'))
    team: Mapped[Optional["Team"]] = db.relationship(back_populates='members')
    name: Mapped[str] = mapped_column(db.String(255))

