"""empty message

Revision ID: 472181ca1b04
Revises: 2156d16a6e6a
Create Date: 2022-08-05 01:30:45.009781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '472181ca1b04'
down_revision = '2156d16a6e6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
