"""Support multi-product orders and track product stock quantity.

Revision ID: 9f179f775a85
Revises: 244329ed368a
Create Date: 2025-10-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f179f775a85'
down_revision: Union[str, Sequence[str], None] = '244329ed368a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'))
    op.alter_column('products', 'stock_quantity', server_default=None)

    op.drop_column('orders', 'product_id')
    op.drop_column('orders', 'quantity')

    op.create_table(
        'order_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('order_id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('order_items')

    op.add_column('orders', sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('orders', sa.Column('product_id', sa.Uuid(), nullable=False))
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products', ['product_id'], ['id'])

    op.drop_column('products', 'stock_quantity')
