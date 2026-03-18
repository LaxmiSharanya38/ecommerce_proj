"""add coupon columns to cart

Revision ID: 66c8f1ee26ec
Revises: ee7c048d3f5a
Create Date: 2026-03-18 15:32:36.767675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66c8f1ee26ec'
down_revision: Union[str, Sequence[str], None] = 'ee7c048d3f5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Add columns ----
    op.add_column(
        'carts',
        sa.Column('coupon_id', sa.UUID(), nullable=True)
    )

    op.add_column(
        'carts',
        sa.Column('discount_amount',
                  sa.Numeric(precision=10, scale=2),
                  nullable=True)
    )

    op.add_column(
        'carts',
        sa.Column('final_amount',
                  sa.Numeric(precision=10, scale=2),
                  nullable=True)
    )

    # ---- Foreign Key ----
    op.create_foreign_key(
        'fk_carts_coupon',
        'carts',
        'coupons',
        ['coupon_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # ---- Drop FK ----
    op.drop_constraint(
        'fk_carts_coupon',
        'carts',
        type_='foreignkey'
    )

    # ---- Drop columns ----
    op.drop_column('carts', 'final_amount')
    op.drop_column('carts', 'discount_amount')
    op.drop_column('carts', 'coupon_id')