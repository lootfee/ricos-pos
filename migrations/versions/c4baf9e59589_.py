"""empty message

Revision ID: c4baf9e59589
Revises: 48fb02473c1c
Create Date: 2023-02-23 02:25:41.008354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4baf9e59589'
down_revision = '48fb02473c1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_per_piece', sa.Numeric(precision=10, scale=2), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory', schema=None) as batch_op:
        batch_op.drop_column('price_per_piece')

    # ### end Alembic commands ###