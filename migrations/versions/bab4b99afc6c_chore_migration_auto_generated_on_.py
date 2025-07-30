"""chore(migration): combine mission_status + door enums
Revision ID: bab4b99afc6c
Revises: de17c545e41d
Create Date: 2025-07-30 13:18:00.811358
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Enum as SAEnum


# revision identifiers, used by Alembic.
revision: str = "bab4b99afc6c"
down_revision: Union[str, None] = "de17c545e41d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# re‑usable Enum definitions
door_enum: SAEnum = SAEnum(
    "Ledningscentralen",
    "Ambassaden",
    "Syster Kents",
    "Hilbert Cafe",
    "Cafeförrådet",
    "Pubförrådet",
    "Sopkomprimatorn",
    "Arkivet",
    name="door_enum",
    native_enum=False,
)


def upgrade() -> None:
    op.execute("CREATE TYPE IF NOT EXISTS mission_status AS ENUM ('Accepted','Failed','Review')")
    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table",
        sa.Column(
            "is_accepted",
            postgresql.ENUM("Accepted", "Failed", "Review", name="mission_status", create_type=False),
            nullable=False,
            server_default=sa.text("'Review'"),
        ),
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    for table in ("post_door_access_table", "user_door_access_table"):
        op.alter_column(
            table,
            "door",
            existing_type=sa.VARCHAR(length=12),
            type_=door_enum,
            existing_nullable=False,
        )


def downgrade() -> None:
    for table in ("user_door_access_table", "post_door_access_table"):
        op.alter_column(
            table,
            "door",
            existing_type=door_enum,
            type_=sa.VARCHAR(length=12),
            existing_nullable=False,
        )

    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table", sa.Column("is_accepted", sa.Boolean, nullable=False, server_default=sa.text("FALSE"))
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    # 3) Drop the ENUM type only if it exists
    op.execute("DROP TYPE IF EXISTS mission_status")
