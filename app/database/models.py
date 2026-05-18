import uuid

from sqlalchemy import UUID, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    # Naming convention to avoid alembic conflicts
    # https://docs.sqlalchemy.org/en/20/core/constraints.html#constraint-naming-conventions
    metadata = MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        }
    )

    # Does not support joined-table inheritance
    # In that case, subclasses must override `id` and define: ForeignKey(parent.id, primary_key=True)
    # See example: https://flask-sqlalchemy.readthedocs.io/en/stable/customizing/#model-class
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
