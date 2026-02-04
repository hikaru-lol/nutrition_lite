"""remove meal recommendation unique constraint and add performance indexes

Revision ID: ecdd67ebcfe9
Revises: a62e2bce09fb
Create Date: 2026-02-03 18:05:44.882775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ecdd67ebcfe9'
down_revision: Union[str, Sequence[str], None] = 'a62e2bce09fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint and add performance indexes."""

    # 1. Remove the unique constraint that prevents multiple recommendations per day
    op.drop_constraint(
        "uq_meal_recommendation_user_date",
        "meal_recommendations",
        type_="unique"
    )

    # 2. Add performance indexes for new query patterns
    op.create_index(
        "idx_meal_rec_user_created",
        "meal_recommendations",
        ["user_id", "created_at"],
        postgresql_ops={"created_at": "DESC"}
    )

    op.create_index(
        "idx_meal_rec_user_date_created",
        "meal_recommendations",
        ["user_id", "generated_for_date", "created_at"],
        postgresql_ops={"created_at": "DESC"}
    )


def downgrade() -> None:
    """Restore unique constraint and remove performance indexes."""

    # Remove performance indexes
    op.drop_index("idx_meal_rec_user_created", "meal_recommendations")
    op.drop_index("idx_meal_rec_user_date_created", "meal_recommendations")

    # Restore unique constraint (this may fail if duplicate data exists)
    op.create_unique_constraint(
        "uq_meal_recommendation_user_date",
        "meal_recommendations",
        ["user_id", "generated_for_date"]
    )
