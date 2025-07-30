"""chore(migration): combine mission_status + door enums
Revision ID: bab4b99afc6c
Revises: de17c545e41d
Create Date: 2025-07-30 13:18:00.811358
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy import Enum as SAEnum, text

# revision identifiers, used by Alembic.
revision: str = "bab4b99afc6c"
down_revision: Union[str, None] = "de17c545e41d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# define two Enum objects:
#  • one to CREATE/DROP (no create_type flag)
#  • one to use in the Column (create_type=False so SQLAlchemy won’t try to re-emit DDL)
create_mission_status = PG_ENUM("Accepted", "Failed", "Review", name="mission_status")
mission_status = PG_ENUM("Accepted", "Failed", "Review", name="mission_status", create_type=False)

door_enum = SAEnum(
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
    # 1) Create the PG enum only if it doesn't already exist
    create_mission_status.create(op.get_bind(), checkfirst=True)

    # 2) Drop the old boolean, add the new enum column
    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table",
        sa.Column(
            "is_accepted",
            mission_status,
            nullable=False,
            server_default=text("'Review'"),
        ),
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    # 3) Convert door columns to non-native ENUMs
    for table in ("post_door_access_table", "user_door_access_table"):
        op.alter_column(
            table,
            "door",
            existing_type=sa.VARCHAR(length=12),
            type_=door_enum,
            existing_nullable=False,
        )


def downgrade() -> None:
    # 1) Revert door columns back to VARCHAR
    for table in ("user_door_access_table", "post_door_access_table"):
        op.alter_column(
            table,
            "door",
            existing_type=door_enum,
            type_=sa.VARCHAR(length=12),
            existing_nullable=False,
        )

    # 2) Drop the enum‐backed column, re-add the old Boolean
    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table",
        sa.Column(
            "is_accepted",
            sa.Boolean,
            nullable=False,
            server_default=text("FALSE"),
        ),
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    # 3) Drop the PG enum if it's still there
    create_mission_status.drop(op.get_bind(), checkfirst=True)
