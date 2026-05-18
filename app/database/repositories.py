from collections.abc import Sequence
from typing import Any

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy import event, exists, func
from sqlalchemy.orm import DeclarativeBase, Mapper
from sqlalchemy.sql import Select
from werkzeug.local import LocalProxy


@event.listens_for(Mapper, 'instrument_class')
def attach_repositories(mapper, cls):
    if 'objects' not in cls.__dict__:
        cls.objects = Repository(cls)


class Repository[T: DeclarativeBase]:
    db: LocalProxy[SQLAlchemy] = LocalProxy(lambda: current_app.extensions['sqlalchemy'])
    meta: type[T]

    def __init__(self, model: type[T]):
        self.model = model

    @property
    def session(self) -> Session:
        return self.db.session

    def select(self) -> Select[Any]:
        return self.db.select(self.model)

    def create(self, flush: bool = True, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)

        if flush:
            self.session.flush()

        return instance

    def bulk_create(self, records: list[dict[str, Any]], flush: bool = True) -> Sequence[T]:
        instances = [self.model(**data) for data in records]
        self.session.add_all(instances)

        if flush:
            self.session.flush()

        return instances

    def save(self, instance: T, flush: bool = True) -> T:
        self.session.add(instance)

        if flush:
            self.session.flush()

        return instance

    def update(self, instance: T, flush: bool = True, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)

        self.session.add(instance)

        if flush:
            self.session.flush()

        return instance

    def delete(self, instance: T, flush: bool = True) -> None:
        self.session.delete(instance)

        if flush:
            self.session.flush()

    def get(self, pk: Any) -> T | None:
        return self.session.get(self.model, pk)

    def get_or_404(self, pk: Any) -> T:
        return self.db.get_or_404(self.model, pk)

    def one(self, **kwargs) -> T:
        stmt = self.select().filter_by(**kwargs)
        return self.session.execute(stmt).scalar_one()

    def one_or_none(self, **kwargs) -> T | None:
        stmt = self.select().filter_by(**kwargs)
        return self.session.execute(stmt).scalar_one_or_none()

    def first(self, **kwargs) -> T | None:
        stmt = self.select().filter_by(**kwargs)
        return self.session.execute(stmt).scalars().first()

    def all(self) -> Sequence[T]:
        stmt = self.select()
        return self.session.scalars(stmt).all()

    def filter(self, **kwargs) -> Sequence[T]:
        stmt = self.select().filter_by(**kwargs)
        return self.session.scalars(stmt).all()

    def where(self, *criteria) -> Sequence[T]:
        stmt = self.select().where(*criteria)
        return self.session.scalars(stmt).all()

    def count(self, *criteria) -> int:
        stmt = self.db.select(func.count()).select_from(self.model)

        if criteria:
            stmt = stmt.where(*criteria)

        return self.session.execute(stmt).scalar_one()

    def exists(self, **filters) -> bool:
        stmt = self.db.select(exists(self.select().filter_by(**filters)))
        return bool(self.session.scalar(stmt))

    def paginate(self, page: int = 1, per_page: int = 20, *criteria, **filters) -> dict[str, Any]:
        stmt = self.select()

        if criteria:
            stmt = stmt.where(*criteria)
        if filters:
            stmt = stmt.filter_by(**filters)

        pagination = self.db.paginate(stmt, page=page, per_page=per_page)

        return {
            'items': pagination.items,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
