"""empty message

Revision ID: 337890d750d6
Revises: 2f08f1e6e15f
Create Date: 2020-10-12 15:07:46.257090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '337890d750d6'
down_revision = '2f08f1e6e15f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('auth_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.drop_column('users', 'nickname')
    op.drop_column('users', 'github_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('github_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('nickname', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'username')
    op.drop_column('users', 'name')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'auth_id')
    # ### end Alembic commands ###
