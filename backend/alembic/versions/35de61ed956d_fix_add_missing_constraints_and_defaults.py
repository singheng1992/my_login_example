"""fix_add_missing_constraints_and_defaults

Revision ID: 35de61ed956d
Revises: e61f7057779f
Create Date: 2026-01-13 19:05:38.448922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '35de61ed956d'
down_revision: Union[str, None] = 'e61f7057779f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加唯一约束
    op.create_unique_constraint('uq_oauth_provider_user_id', 'oauth_accounts', ['provider', 'provider_user_id'])

    # 设置is_deleted字段的默认值
    op.alter_column('users', 'is_deleted', server_default=text('FALSE'))
    op.alter_column('oauth_accounts', 'is_deleted', server_default=text('FALSE'))
    op.alter_column('verification_codes', 'is_deleted', server_default=text('FALSE'))

    # 设置used字段的默认值
    op.alter_column('verification_codes', 'used', server_default=text('FALSE'))


def downgrade() -> None:
    # 删除唯一约束
    op.drop_constraint('uq_oauth_provider_user_id', 'oauth_accounts', type_='unique')

    # 移除默认值
    op.alter_column('users', 'is_deleted', server_default=None)
    op.alter_column('oauth_accounts', 'is_deleted', server_default=None)
    op.alter_column('verification_codes', 'is_deleted', server_default=None)
    op.alter_column('verification_codes', 'used', server_default=None)
