"""baseline schema

Revision ID: 0001_baseline
Revises:
Create Date: 2026-04-27
"""
from alembic import op

from app.database import Base
from app.models import *  # noqa: F401,F403

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
