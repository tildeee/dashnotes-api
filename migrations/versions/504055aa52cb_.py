"""empty message

Revision ID: 504055aa52cb
Revises: 
Create Date: 2020-10-05 23:15:18.279201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '504055aa52cb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stickies')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stickies',
    sa.Column('id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='stickies_pkey')
    )
    # ### end Alembic commands ###
