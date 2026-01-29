"""
API Keys Router
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreated
from app.services.api_key_service import APIKeyService
from app.utils.security import get_current_user

router = APIRouter()


@router.post("", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new API key.
    
    **Important**: The full API key is only shown once on creation.
    Store it securely as it cannot be retrieved later.
    
    - **name**: Name/identifier for the API key
    - **description**: Optional description
    - **expires_in_days**: Optional expiration (1-365 days)
    """
    api_key_service = APIKeyService(db)
    
    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
    
    # Generate API key
    api_key, raw_key = await api_key_service.create_api_key(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        expires_at=expires_at
    )
    
    return APIKeyCreated(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        description=api_key.description,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        api_key=raw_key  # Only returned on creation
    )


@router.get("", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all API keys for the current user.
    
    Note: The full API key is not included in the response for security.
    """
    query = select(APIKey).where(APIKey.user_id == current_user.id)
    result = await db.execute(query)
    api_keys = result.scalars().all()
    
    return api_keys


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get API key details by ID.
    """
    query = select(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    )
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke (delete) an API key.
    
    This action is irreversible. The API key will immediately stop working.
    """
    query = select(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    )
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    await db.delete(api_key)
    await db.commit()


@router.patch("/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate an API key (can be reactivated later).
    """
    query = select(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    )
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    await db.commit()
    await db.refresh(api_key)
    
    return api_key


@router.patch("/{key_id}/activate", response_model=APIKeyResponse)
async def activate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate a deactivated API key.
    """
    query = select(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    )
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = True
    await db.commit()
    await db.refresh(api_key)
    
    return api_key
