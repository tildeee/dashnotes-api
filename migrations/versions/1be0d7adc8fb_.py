"""empty message

Revision ID: 1be0d7adc8fb
Revises: 337890d750d6
Create Date: 2020-10-12 19:53:53.402545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1be0d7adc8fb'
down_revision = '337890d750d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stickies', sa.Column('user_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stickies', 'user_id')
    # ### end Alembic commands ###
