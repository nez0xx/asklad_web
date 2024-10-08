"""empty message

Revision ID: f9a889dde083
Revises: 61a28e39403e
Create Date: 2024-08-12 17:15:59.067217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9a889dde083'
down_revision: Union[str, None] = '61a28e39403e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('warehouses', 'created_at',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('warehouses', 'created_at',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    # ### end Alembic commands ###
