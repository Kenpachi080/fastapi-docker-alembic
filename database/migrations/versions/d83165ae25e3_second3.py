"""Second3

Revision ID: d83165ae25e3
Revises: e8518f3fd09b
Create Date: 2021-12-20 13:11:48.829065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd83165ae25e3'
down_revision = 'e8518f3fd09b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todo',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('content', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('content')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('todo')
    # ### end Alembic commands ###