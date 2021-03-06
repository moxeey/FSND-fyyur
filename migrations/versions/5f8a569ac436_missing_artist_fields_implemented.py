"""missing Artist fields implemented

Revision ID: 5f8a569ac436
Revises: a9233783b3b6
Create Date: 2022-05-30 00:52:51.999531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f8a569ac436'
down_revision = 'a9233783b3b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artists', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Artists', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artists', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artists', 'seeking_description')
    op.drop_column('Artists', 'seeking_venue')
    op.drop_column('Artists', 'website')
    # ### end Alembic commands ###
