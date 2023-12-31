"""empty message

Revision ID: 2d5cf4dc0c93
Revises: 9326096e127b
Create Date: 2023-12-06 12:58:46.463225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d5cf4dc0c93'
down_revision = '9326096e127b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('password_token', schema=None) as batch_op:
        batch_op.add_column(sa.Column('userEmail', sa.String(length=120), nullable=False))
        batch_op.create_unique_constraint(None, ['id'])
        batch_op.drop_constraint('password_token_userId_fkey', type_='foreignkey')
        batch_op.drop_column('userId')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('password_token', schema=None) as batch_op:
        batch_op.add_column(sa.Column('userId', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('password_token_userId_fkey', 'user', ['userId'], ['id'])
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('userEmail')

    # ### end Alembic commands ###
