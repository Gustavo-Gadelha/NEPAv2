from typing import Any

from app.extensions import db
from app.features.auth.models import ObjectPermission, Permission, Role, User


def assign_perm(role: Role, perm: str) -> None:
    permission = db.session.scalar(db.select(Permission).where(Permission.name == perm))

    if permission is None:
        raise ValueError(f"Permission '{perm}' does not exist")

    if permission not in role.permissions:
        role.permissions.append(permission)


def assign_object_perm(user: User, perm: str, obj: Any) -> ObjectPermission:
    permission = db.session.scalar(db.select(Permission).where(Permission.name == perm))

    if permission is None:
        raise ValueError(f"Permission '{perm}' does not exist")

    existing = db.session.scalar(
        db.select(ObjectPermission).where(
            ObjectPermission.user_id == user.id,
            ObjectPermission.permission_id == permission.id,
            ObjectPermission.object_type == type(obj).__name__,
            ObjectPermission.object_id == obj.id,
        )
    )

    if existing:
        return existing

    object_permission = ObjectPermission(
        user_id=user.id,
        permission_id=permission.id,
        object_type=type(obj).__name__,
        object_id=obj.id,
    )

    db.session.add(object_permission)
    return object_permission
