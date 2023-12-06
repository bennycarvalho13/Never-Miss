"""empty message

Revision ID: 9326096e127b
Revises: e03f1453ff7e
Create Date: 2023-12-06 12:51:31.554758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9326096e127b'
down_revision = 'e03f1453ff7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('password_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('token', sa.String(length=120), nullable=False),
    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('password_token')
    # ### end Alembic commands ###
