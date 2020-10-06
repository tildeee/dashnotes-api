"""empty message

Revision ID: 856cac3e13a8
Revises: 504055aa52cb
Create Date: 2020-10-05 23:20:35.335712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '856cac3e13a8'
down_revision = '504055aa52cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stickies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stickies')
    # ### end Alembic commands ###
