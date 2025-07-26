"""chore(migration): auto-generated on fb619c3dc9601ac937ac2220d48a083c604bde59

Revision ID: 0a77ff84dca2
Revises: 05bcabd34057
Create Date: 2025-07-26 15:54:32.871453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a77ff84dca2'
down_revision: Union[str, None] = '05bcabd34057'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_table',
        sa.Column('moose_game_name', sa.String(), nullable=False, server_default=''))
    op.add_column('user_table',
        sa.Column('moose_game_score', sa.Integer(), nullable=False, server_default='0')
    )

def downgrade():
    op.drop_column('user_table', 'moose_game_score')
    op.drop_column('user_table', 'moose_game_name')


