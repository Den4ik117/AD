"""Add order reports table.

Revision ID: 4a46ef2a64bd
Revises: 9f179f775a85
Create Date: 2025-10-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a46ef2a64bd'
down_revision: Union[str, Sequence[str], None] = '9f179f775a85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'order_reports',
        sa.Column('report_at', sa.Date(), nullable=False),
        sa.Column('order_id', sa.Uuid(), nullable=False),
        sa.Column('count_product', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('report_at', 'order_id'),
    )
    op.create_index(
        'ix_order_reports_report_at',
        'order_reports',
        ['report_at'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_order_reports_report_at', table_name='order_reports')
    op.drop_table('order_reports')
