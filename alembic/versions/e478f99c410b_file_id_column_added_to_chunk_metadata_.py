"""file_id column added to chunk_metadata table

Revision ID: e478f99c410b
Revises: 0e9e6ed48318
Create Date: 2025-05-14 18:02:43.573407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e478f99c410b'
down_revision: Union[str, None] = '0e9e6ed48318'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chunk_metadata', sa.Column('file_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'chunk_metadata', 'file_metadata', ['file_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'chunk_metadata', type_='foreignkey')
    op.drop_column('chunk_metadata', 'file_id')
    # ### end Alembic commands ###
