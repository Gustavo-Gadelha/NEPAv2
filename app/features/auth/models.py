from datetime import UTC, datetime
from typing import Any

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ObjectPermission(db.Model):
    __tablename__ = 'object_permissions'

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'perm_id',
            'object_type',
            'object_id',
        ),
    )

    object_type: Mapped[str] = mapped_column(db.String)
    object_id: Mapped[UUID] = mapped_column(db.UUID)

    user_id: Mapped[UUID] = mapped_column(db.ForeignKey('user_accounts.id', ondelete='CASCADE'))
    perm_id: Mapped[UUID] = mapped_column(db.ForeignKey('permissions.id', ondelete='CASCADE'))

    user: Mapped[User | None] = relationship(back_populates='object_permissions')


role_permissions = db.Table(
    'role_permissions',
    db.metadata,
    db.Column('role_id', db.UUID, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.UUID, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
)


class Permission(db.Model):
    __tablename__ = 'permissions'

    name: Mapped[str] = mapped_column(db.String, unique=True)
    description: Mapped[str | None] = mapped_column(db.Text)

    def __repr__(self) -> str:
        return f'<Permission {self.name}>'


user_roles = db.Table(
    'user_roles',
    db.metadata,
    db.Column('user_id', db.UUID, db.ForeignKey('user_accounts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('role_id', db.UUID, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)


class Role(db.Model):
    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(db.String, unique=True)
    description: Mapped[str | None] = mapped_column(db.Text)
    permissions: Mapped[list[Permission]] = relationship(secondary=role_permissions, lazy='selectin')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class User(db.Model):
    __tablename__ = 'user_accounts'

    email: Mapped[str] = mapped_column(db.String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(db.String(64), unique=True, index=True)
    password: Mapped[str | None] = mapped_column(db.String(255))
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=True)

    confirmed_email: Mapped[bool] = mapped_column(db.Boolean, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))

    tfa_primary_method: Mapped[str | None] = mapped_column(db.String)
    tfa_totp_secret: Mapped[str | None] = mapped_column(db.String)

    token_secret: Mapped[str | None] = mapped_column(db.String)

    reset_password_token: Mapped[str | None] = mapped_column(unique=True, index=True)
    reset_password_sent_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))

    first_name: Mapped[str | None] = mapped_column(db.String(64))
    last_name: Mapped[str | None] = mapped_column(db.String(64))
    avatar_url: Mapped[str | None] = mapped_column(db.String(512))
    timezone: Mapped[str] = mapped_column(db.String(64), default='UTC')

    last_login_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))
    current_login_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))
    last_login_ip: Mapped[str | None] = mapped_column(db.String)
    current_login_ip: Mapped[str | None] = mapped_column(db.String)
    login_count: Mapped[int] = mapped_column(db.Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    roles: Mapped[list[Role]] = relationship(secondary=user_roles, lazy='selectin')
    object_permissions: Mapped[list[ObjectPermission]] = relationship(back_populates='user')

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    def has_role(self, role: str) -> bool:
        return any(role == r.name for r in self.roles)

    def has_roles(self, roles: list[str]) -> bool:
        return all(self.has_role(role) for role in roles)

    def has_perm(self, perm: str) -> bool:
        return any(perm == p.name for role in self.roles for p in role.permissions)

    def has_perms(self, perms: list[str]) -> bool:
        return all(self.has_perm(perm) for perm in perms)

    def has_object_perm(self, perm: str, obj: Any) -> bool:
        stmt = (
            db.select(ObjectPermission)
            .join(ObjectPermission.permission)
            .where(
                ObjectPermission.user_id == self.id,
                ObjectPermission.object_type == type(obj).__name__,
                ObjectPermission.object_id == obj.id,
                Permission.name == perm,
            )
        )

        return db.session.scalar(stmt) is not None

    def invalidate_tokens(self) -> None:
        self.token_secret = None

    def __repr__(self) -> str:
        return f'<User {self.email}>'
