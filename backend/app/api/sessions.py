from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.core.security import decode_access_token
from app.schemas.common import ApiResponse
from app.models.session import Session as SessionModel

router = APIRouter()
security = HTTPBearer()


@router.get("/sessions", response_model=ApiResponse[List[Dict]])
async def get_sessions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有活跃会话"""
    result = await db.execute(
        select(SessionModel).where(
            SessionModel.user_id == user_id,
            SessionModel.is_revoked == False,
            SessionModel.is_deleted == False
        ).order_by(SessionModel.created_at.desc())
    )
    sessions = result.scalars().all()

    session_list = []
    for session in sessions:
        session_list.append({
            "id": str(session.id),
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "created_at": session.created_at.isoformat(),
            "last_used_at": session.last_used_at.isoformat() if session.last_used_at else None,
            "expires_at": session.expires_at.isoformat()
        })

    return ApiResponse(data=session_list)


@router.post("/sessions/{session_id}/revoke", response_model=ApiResponse[Dict])
async def revoke_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """撤销指定的会话"""
    result = await db.execute(
        select(SessionModel).where(
            and_(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.is_revoked == False
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.is_revoked = True
    session.revoked_at = datetime.utcnow()
    await db.commit()

    return ApiResponse(message="会话已撤销")


@router.post("/sessions/revoke-others", response_model=ApiResponse[Dict])
async def revoke_other_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """撤销除当前会话外的所有其他会话"""
    # 获取当前 token 的 jti
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    current_jti = payload.get("jti")

    # 撤销除当前 jti 外的所有会话
    result = await db.execute(
        select(SessionModel).where(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.token_jti != current_jti,
                SessionModel.is_revoked == False
            )
        )
    )
    sessions = result.scalars().all()

    for session in sessions:
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()

    await db.commit()

    return ApiResponse(message=f"已撤销 {len(sessions)} 个其他会话")
