"""Cancelled_at and refund_status added

Revision ID: 04c4b9a4abee
Revises: d3454901e315
Create Date: 2026-03-17 10:30:59.476851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04c4b9a4abee'
down_revision: Union[str, Sequence[str], None] = 'd3454901e315'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1️⃣ Create the enum type in PostgreSQL
    refund_enum = sa.Enum("NONE", "PENDING", "COMPLETED", "FAILED", name="refund_status_enum")
    refund_enum.create(op.get_bind(), checkfirst=True)

    # Add cancelled_at column
    op.add_column('orders', sa.Column('cancelled_at', sa.DateTime(), nullable=True))

    # Add refund_status column
    op.add_column(
        'orders',
        sa.Column(
            'refund_status',
            refund_enum,
            nullable=False,
            server_default="NONE"
        )
    )

def downgrade():
    op.drop_column('orders', 'cancelled_at')
    op.drop_column('orders', 'refund_status')
    sa.Enum(name='refund_status_enum').drop(op.get_bind(), checkfirst=True)