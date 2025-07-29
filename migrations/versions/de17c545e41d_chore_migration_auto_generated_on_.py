from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'de17c545e41d'
down_revision = '58ef994bb4f9'
branch_labels = None
depends_on = None

# define the new enum type
STATUS_ENUM = sa.Enum('Accepted', 'Failed', 'Review', name='mission_status')

def upgrade() -> None:
    # 1) Drop the old boolean column (data is lost)
    op.drop_column('group_mission_table', 'is_accepted')

    # 2) Create the enum type
    STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    # 3) Add the new column, defaulting to 'Review' so existing rows aren’t NULL
    op.add_column(
        'group_mission_table',
        sa.Column(
            'is_accepted',
            STATUS_ENUM,
            nullable=False,
            server_default=sa.text("'Review'")
        )
    )
    # 4) (optional) remove the server_default if you don’t want it permanent
    op.alter_column(
        'group_mission_table',
        'is_accepted',
        server_default=None
    )


def downgrade() -> None:
    # 1) Drop the enum column
    op.drop_column('group_mission_table', 'is_accepted')

    # 2) Re-create the Boolean column (you may choose a default of FALSE)
    op.add_column(
        'group_mission_table',
        sa.Column(
            'is_accepted',
            sa.Boolean,
            nullable=False,
            server_default=sa.text('FALSE')
        )
    )
    op.alter_column(
        'group_mission_table',
        'is_accepted',
        server_default=None
    )

    # 3) Drop the enum type
    STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
