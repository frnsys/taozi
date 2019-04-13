"""empty message

Revision ID: 51a5f39b3cad
Revises: baa981684b35
Create Date: 2019-04-12 22:13:05.575058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51a5f39b3cad'
down_revision = 'baa981684b35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subtitle', sa.Unicode(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('subtitle')

    # ### end Alembic commands ###