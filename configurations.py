"""
Configurations Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.configuration import Configuration
from app.utils.security import get_current_user, require_role

router = APIRouter()


class ConfigCreate(BaseModel):
    key: str
    value: str
    value_type: str = "string"
    description: Optional[str] = None
    is_sensitive: bool = False


class ConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None


class ConfigResponse(BaseModel):
    id: int
    key: str
    value: str
    value_type: str
    description: Optional[str]
    is_sensitive: bool
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ConfigResponse])
async def list_configurations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all configurations.
    
    Sensitive values are masked for non-admin users.
    """
    query = select(Configuration).where(Configuration.is_active == True)
    
    if search:
        query = query.where(Configuration.key.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    configs = result.scalars().all()
    
    # Mask sensitive values for non-admins
    response = []
    for config in configs:
        config_dict = {
            "id": config.id,
            "key": config.key,
            "value": config.value if not config.is_sensitive or current_user.role == UserRole.ADMIN else "********",
            "value_type": config.value_type,
            "description": config.description,
            "is_sensitive": config.is_sensitive,
            "is_active": config.is_active
        }
        response.append(ConfigResponse(**config_dict))
    
    return response


@router.get("/{key}", response_model=ConfigResponse)
async def get_configuration(
    key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get configuration by key.
    """
    query = select(Configuration).where(Configuration.key == key)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Mask sensitive value for non-admins
    value = config.value
    if config.is_sensitive and current_user.role != UserRole.ADMIN:
        value = "********"
    
    return ConfigResponse(
        id=config.id,
        key=config.key,
        value=value,
        value_type=config.value_type,
        description=config.description,
        is_sensitive=config.is_sensitive,
        is_active=config.is_active
    )


@router.post("", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_configuration(
    request: ConfigCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new configuration (Admin/Manager only).
    """
    # Check if key exists
    existing = await db.execute(
        select(Configuration).where(Configuration.key == request.key)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configuration key already exists"
        )
    
    config = Configuration(
        key=request.key,
        value=request.value,
        value_type=request.value_type,
        description=request.description,
        is_sensitive=request.is_sensitive,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return config


@router.put("/{key}", response_model=ConfigResponse)
async def update_configuration(
    key: str,
    request: ConfigUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update configuration by key (Admin/Manager only).
    """
    query = select(Configuration).where(Configuration.key == key)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    # Update fields
    update_dict = request.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(config, field, value)
    
    config.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(config)
    
    return config


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuration(
    key: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete configuration by key (Admin only).
    """
    query = select(Configuration).where(Configuration.key == key)
    result = await db.execute(query)
    config = result.scalar_one_or_none()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    await db.delete(config)
    await db.commit()
