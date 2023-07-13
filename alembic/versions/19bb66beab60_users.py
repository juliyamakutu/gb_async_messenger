"""Users

Revision ID: 19bb66beab60
Revises: b74ecdccd6b8
Create Date: 2023-07-13 16:27:31.833065

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "19bb66beab60"
down_revision = "b74ecdccd6b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("salt", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
