"""add recommended_meals column to meal_recommendations

Revision ID: a62e2bce09fb
Revises: 736c5c90d610
Create Date: 2026-02-03 17:09:40.424832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a62e2bce09fb'
down_revision: Union[str, Sequence[str], None] = '736c5c90d610'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add recommended_meals JSONB column to meal_recommendations table
    op.add_column('meal_recommendations', sa.Column('recommended_meals', sa.dialects.postgresql.JSONB(), nullable=False, server_default='[]'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove recommended_meals column
    op.drop_column('meal_recommendations', 'recommended_meals')
