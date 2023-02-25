"""empty message

Revision ID: 8a2d31f5fedc
Revises: c4baf9e59589
Create Date: 2023-02-23 20:35:21.947126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a2d31f5fedc'
down_revision = 'c4baf9e59589'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sale',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('date_sold', sa.DateTime(), nullable=True),
    sa.Column('seller_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['seller_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sale_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sale_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('price_per_piece', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_cost', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['sale_id'], ['sale.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sale_item')
    op.drop_table('sale')
    # ### end Alembic commands ###
