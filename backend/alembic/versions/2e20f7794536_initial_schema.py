"""Initial schema

Revision ID: 2e20f7794536
Revises:
Create Date: 2026-09-07 11:02:19.312455

"""

from collections.abc import Sequence

from alembic import op
from app.database.session import Base

# revision identifiers, used by Alembic.
revision: str = "2e20f7794536"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Downgrade schema."""
    Base.metadata.drop_all(bind=op.get_bind())
