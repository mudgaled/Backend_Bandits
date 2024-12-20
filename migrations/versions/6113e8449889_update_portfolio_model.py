"""Update Portfolio model

Revision ID: 6113e8449889
Revises: b54efc30adad
Create Date: 2024-11-15 23:21:03.699141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6113e8449889'
down_revision = 'b54efc30adad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('portfolio', schema=None) as batch_op:
        batch_op.add_column(sa.Column('change', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('portfolio', schema=None) as batch_op:
        batch_op.drop_column('change')

    # ### end Alembic commands ###
