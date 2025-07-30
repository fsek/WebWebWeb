from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy import Enum as SAEnum
from alembic import op
import sqlalchemy as sa

# revision identifiers, etc.
revision = "bab4b99afc6c"
down_revision = "de17c545e41d"

# now Pylance knows this is a PG_ENUM with .create()/.drop()
mission_status: PG_ENUM = PG_ENUM(
    "Accepted",
    "Failed",
    "Review",
    name="mission_status",
    create_type=False,
)

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
    # 1) SQLAlchemy will check pg_type and only CREATE if missing:
    mission_status.create(op.get_bind(), checkfirst=True)

    # 2) Rebuild group_mission_table.is_accepted
    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table",
        sa.Column("is_accepted", mission_status, nullable=False, server_default=sa.text("'Review'")),
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    # 3) Door columns → SA‐ENUM
    for table in ("post_door_access_table", "user_door_access_table"):
        op.alter_column(table, "door", existing_type=sa.VARCHAR(length=12), type_=door_enum, existing_nullable=False)


def downgrade() -> None:
    for table in ("user_door_access_table", "post_door_access_table"):
        op.alter_column(table, "door", existing_type=door_enum, type_=sa.VARCHAR(length=12), existing_nullable=False)

    op.drop_column("group_mission_table", "is_accepted")
    op.add_column(
        "group_mission_table", sa.Column("is_accepted", sa.Boolean, nullable=False, server_default=sa.text("FALSE"))
    )
    op.alter_column("group_mission_table", "is_accepted", server_default=None)

    # drop only if it’s still there
    mission_status.drop(op.get_bind(), checkfirst=True)
