"""empty message

Revision ID: 2001249660da
Revises: c5f68d501ae2
Create Date: 2017-08-20 12:05:47.001263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2001249660da'
down_revision = 'c5f68d501ae2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users_emails',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=80), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_emails')
    # ### end Alembic commands ###