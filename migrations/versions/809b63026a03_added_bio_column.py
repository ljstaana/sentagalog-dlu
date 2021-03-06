"""added bio column

Revision ID: 809b63026a03
Revises: cf6084d2977e
Create Date: 2019-10-13 21:13:10.057216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '809b63026a03'
down_revision = 'cf6084d2977e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bio', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'bio')
    op.add_column('tweets', sa.Column('sentiment', sa.INTEGER(), nullable=True))
    op.add_column('tweets', sa.Column('labeller', sa.INTEGER(), nullable=True))
    op.add_column('tweets', sa.Column('reason_for_sentiment', sa.TEXT(length=64), nullable=True))
    op.drop_index(op.f('ix_tweets_instance_id'), table_name='tweets')
    op.create_table('sqlite_sequence',
    sa.Column('name', sa.NullType(), nullable=True),
    sa.Column('seq', sa.NullType(), nullable=True)
    )
    # ### end Alembic commands ###
