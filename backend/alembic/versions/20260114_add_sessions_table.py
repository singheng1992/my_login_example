"""Add sessions table

Revision ID: 20260114_add_sessions
Revises: 35de61ed956d
Create Date: 2026-01-14 11:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20260114_add_sessions'
down_revision: Union[str, None] = '35de61ed956d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_jti', sa.String(length=255), nullable=False),
        sa.Column('device_info', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_jti')
    )
    op.create_index(op.f('ix_sessions_is_revoked'), 'sessions', ['is_revoked'], unique=False)
    op.create_index(op.f('ix_sessions_is_deleted'), 'sessions', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_sessions_token_jti'), 'sessions', ['token_jti'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_sessions_expires_at'), 'sessions', ['expires_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sessions_expires_at'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_token_jti'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_is_deleted'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_is_revoked'), table_name='sessions')
    op.drop_table('sessions')
