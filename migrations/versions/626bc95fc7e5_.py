"""empty message

Revision ID: 626bc95fc7e5
Revises: 2800b896da69
Create Date: 2023-02-25 14:24:39.323968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '626bc95fc7e5'
down_revision = '2800b896da69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sale', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.String(length=512), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sale', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###