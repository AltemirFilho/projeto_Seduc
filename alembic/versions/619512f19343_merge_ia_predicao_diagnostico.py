"""merge ia: predicao + diagnostico

Revision ID: 619512f19343
Revises: 78c8cd317e01, 56abdbf6064f
Create Date: 2026-06-25 15:14:15.897770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '619512f19343'
down_revision: Union[str, Sequence[str], None] = ('78c8cd317e01', '56abdbf6064f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
