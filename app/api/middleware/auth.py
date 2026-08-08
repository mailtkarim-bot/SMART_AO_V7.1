"""
SMART_AO V7 - auth.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Authentication Middleware
========================================
FastAPI middleware for JWT authentication and RBAC enforcement
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime, timezone
from typing import Callable, Optional, Any, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.auth import get_auth_service
from app.models.user import Role, FINANCIAL_DATA, TECHNICAL_DATA, LEGAL_DATA, ADMIN_DATA, RBAC_RULES
from app.schemas.users import TokenData
from app.core.database import async_get_db
from app.models.user import User
from sqlalchemy import select


# =============================================================================
# OAUTH2 SCHEME
# =============================================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={}
)


# =============================================================================
# CURRENT USER DEPENDENCY
# =============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Any = Depends(async_get_db)
) -> TokenData:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database session
    
    Returns:
        TokenData: Decoded token data with user information
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    auth_service = get_auth_service()
    
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            auth_service.secret_key,
            algorithms=[auth_service.algorithm]
        )
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify user exists and is active
        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is locked",
            )
        
        # Return token data
        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            role=role
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =============================================================================
# RBAC DEPENDENCIES
# =============================================================================

async def get_current_user_with_rbac(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency that enforces RBAC checks on the current user
    
    This is a base dependency that can be extended with specific permissions
    
    Args:
        current_user: TokenData from get_current_user
    
    Returns:
        TokenData: Current user with RBAC context
    """
    return current_user


def check_resource_access(resource_category: str, action: str = "read"):
    """
    Factory function to create permission check dependencies
    
    Args:
        resource_category: Category of resource to check (marge, cctp, etc.)
        action: Action to perform (read, write, delete)
    
    Returns:
        Callable: FastAPI dependency function
    """
    async def dependency(
        current_user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        """
        Check if current user has permission to access the resource
        
        Args:
            current_user: TokenData with user role
        
        Returns:
            TokenData: Current user if access allowed
        
        Raises:
            HTTPException: If access is denied
        """
        # Get user's allowed resources based on role
        user_role = current_user.role
        allowed_resources = RBAC_RULES.get(user_role, [])
        
        # Check if user has access to this resource category
        if resource_category not in allowed_resources:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {resource_category}. Role {user_role} not authorized.",
                headers={"X-RBAC-Denied": "true"},
            )
        
        return current_user
    
    return dependency


# Specific permission dependencies

async def require_financial_access(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency that requires financial data access permission
    
    Only PATRON can access financial data (marges, coefficients, trésorerie)
    
    Args:
        current_user: TokenData from get_current_user
    
    Returns:
        TokenData: Current user if access allowed
    
    Raises:
        HTTPException: If user doesn't have financial access
    """
    user_role = current_user.role
    allowed_resources = RBAC_RULES.get(user_role, [])
    
    # Check if user has access to any financial data category
    has_financial_access = any(
        resource in allowed_resources 
        for resource in FINANCIAL_DATA
    )
    
    if not has_financial_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Financial data requires PATRON role",
            headers={"X-RBAC-Denied": "true"},
        )
    
    return current_user


async def require_admin_access(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency that requires admin access
    
    Only PATRON can access admin functions
    
    Args:
        current_user: TokenData from get_current_user
    
    Returns:
        TokenData: Current user if access allowed
    
    Raises:
        HTTPException: If user doesn't have admin access
    """
    if current_user.role != "patron":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin functions require PATRON role",
            headers={"X-RBAC-Denied": "true"},
        )
    
    return current_user



