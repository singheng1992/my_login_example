"""remove_foreign_keys

Revision ID: 2f4164859f0b
Revises: 20260114_add_sessions
Create Date: 2026-01-14 16:33:04.024955

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f4164859f0b'
down_revision: Union[str, None] = '20260114_add_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 删除 oauth_accounts 表的外键约束
    op.drop_constraint('oauth_accounts_user_id_fkey', 'oauth_accounts', type_='foreignkey')

    # 删除 sessions 表的外键约束
    op.drop_constraint('sessions_user_id_fkey', 'sessions', type_='foreignkey')


def downgrade() -> None:
    # 恢复 oauth_accounts 表的外键约束
    op.create_foreign_key(
        'oauth_accounts_user_id_fkey',
        'oauth_accounts', 'users',
        ['user_id'], ['id']
    )

    # 恢复 sessions 表的外键约束
    op.create_foreign_key(
        'sessions_user_id_fkey',
        'sessions', 'users',
        ['user_id'], ['id']
    )
