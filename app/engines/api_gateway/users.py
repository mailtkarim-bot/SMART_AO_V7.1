"""
SMART_AO V7 - users.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Gestion des utilisateurs - API de gestion des utilisateurs SMART_AO
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData, AuthService, hash_password
from app.models.user import User, Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


class UserCreate(BaseModel):
    """Création d'un nouvel utilisateur."""
    email: EmailStr
    full_name: str
    role: Role
    password: str = Field(min_length=12, description="Mot de passe sécurisé (min 12 caractères)")
    phone: Optional[str] = None
    company: Optional[str] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = None


class UserUpdate(BaseModel):
    """Mise à jour d'un utilisateur."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[Role] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """Réponse utilisateur (sans mot de passe)."""
    user_id: str
    email: EmailStr
    full_name: str
    role: Role
    phone: Optional[str] = None
    company: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class UserListResponse(BaseModel):
    """Liste paginée d'utilisateurs."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class PasswordChange(BaseModel):
    """Changement de mot de passe."""
    current_password: str
    new_password: str = Field(min_length=12)


class PasswordResetRequest(BaseModel):
    """Requête de réinitialisation de mot de passe."""
    email: EmailStr


class UserStats(BaseModel):
    """Statistiques utilisateurs."""
    total_users: int
    active_users: int
    users_by_role: Dict[str, int]
    recent_signups: int
    last_24h: int


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un nouvel utilisateur.
    
    Restreint aux administrateurs.
    """
    logger.info(f"Création utilisateur: {user_data.email} par {current_user.email}")
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent créer des utilisateurs"
        )
    
    # Vérifier si l'email existe déjà
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Hash du mot de passe
    hashed_password = hash_password(user_data.password)
    
    # Créer le nouvel utilisateur
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hashed_password,
        phone=user_data.phone,
        company=user_data.company,
        is_active=user_data.is_active,
        metadata=user_data.metadata
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        phone=new_user.phone,
        company=new_user.company,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_login=new_user.last_login,
        metadata=new_user.metadata
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère le profil de l'utilisateur courant."""
    logger.info(f"Profil utilisateur: {current_user.user_id}")
    
    result = await db.execute(
        select(User).where(User.user_id == current_user.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        company=user.company,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        metadata=user.metadata
    )


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 50,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Liste les utilisateurs avec pagination.
    
    Restreint aux administrateurs.
    """
    logger.info(f"Liste utilisateurs par {current_user.email}")
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent lister les utilisateurs"
        )
    
    offset = (page - 1) * page_size
    
    # Construire la requête
    query = select(User)
    
    if role is not None:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
                User.company.ilike(search_pattern)
            )
        )
    
    # Compter le total
    count_result = await db.execute(select(User).where(*query.where_clauses))
    total = len(count_result.scalars().all())
    
    # Récupérer la page
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[
            UserResponse(
                user_id=u.user_id,
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                phone=u.phone,
                company=u.company,
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
                last_login=u.last_login,
                metadata=u.metadata
            ) for u in users
        ],
        total=total,
        page=page,
        page_size=page_size,
        has_more=offset + page_size < total
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'un utilisateur.
    
    Restreint aux administrateurs ou à l'utilisateur lui-même.
    """
    logger.info(f"Détails utilisateur: {user_id} par {current_user.user_id}")
    
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier les permissions
    if current_user.user_id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        company=user.company,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        metadata=user.metadata
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour un utilisateur.
    
    Restreint aux administrateurs ou à l'utilisateur lui-même (pour ses propres données).
    """
    logger.info(f"Mise à jour utilisateur: {user_id} par {current_user.user_id}")
    
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier les permissions
    if current_user.user_id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    # Limiter les mises à jour pour les non-admins
    if current_user.role != Role.ADMIN:
        # Les utilisateurs non-admins ne peuvent pas changer leur rôle ou statut
        if user_data.role is not None or user_data.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les administrateurs peuvent modifier le rôle ou le statut"
            )
    
    # Appliquer les mises à jour
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.company is not None:
        user.company = user_data.company
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.metadata is not None:
        user.metadata = user_data.metadata
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        company=user.company,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
        metadata=user.metadata
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime un utilisateur.
    
    Restreint aux administrateurs.
    """
    logger.info(f"Suppression utilisateur: {user_id} par {current_user.email}")
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent supprimer des utilisateurs"
        )
    
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    await db.delete(user)
    await db.commit()


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: str,
    password_data: PasswordChange,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change le mot de passe d'un utilisateur.
    
    Restreint à l'utilisateur lui-même ou aux administrateurs.
    """
    logger.info(f"Changement mot de passe: {user_id} par {current_user.user_id}")
    
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier les permissions
    if current_user.user_id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    # Vérifier l'ancien mot de passe (sauf pour les admins qui changent le mot de passe d'autres utilisateurs)
    if current_user.user_id == user_id:
        auth_service = AuthService()
        if not auth_service.verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ancien mot de passe incorrect"
            )
    
    # Hash du nouveau mot de passe
    user.hashed_password = hash_password(password_data.new_password)
    
    await db.commit()


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    request: PasswordResetRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Réinitialise le mot de passe d'un utilisateur.
    
    Restreint aux administrateurs.
    """
    logger.info(f"Réinitialisation mot de passe: {request.email} par {current_user.email}")
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent réinitialiser les mots de passe"
        )
    
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Générer un mot de passe temporaire (en production, envoyer un email)
    temp_password = "TempPass123!@#"
    user.hashed_password = hash_password(temp_password)
    
    await db.commit()


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les statistiques utilisateurs.
    
    Restreint aux administrateurs.
    """
    logger.info(f"Statistiques utilisateurs par {current_user.email}")
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent consulter les statistiques"
        )
    
    # Compter les utilisateurs
    result = await db.execute(select(User))
    all_users = result.scalars().all()
    total_users = len(all_users)
    active_users = sum(1 for u in all_users if u.is_active)
    
    # Compter par rôle
    users_by_role = {}
    for role in Role:
        users_by_role[role.value] = sum(1 for u in all_users if u.role == role)
    
    # Utilisateurs récents (derniers 7 jours)
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_signups = sum(1 for u in all_users if u.created_at >= recent_cutoff)
    
    # Utilisateurs actifs dans les dernières 24h
    last_24h_cutoff = datetime.utcnow() - timedelta(hours=24)
    last_24h = sum(1 for u in all_users if u.last_login and u.last_login >= last_24h_cutoff)
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        users_by_role=users_by_role,
        recent_signups=recent_signups,
        last_24h=last_24h
    )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "users",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

