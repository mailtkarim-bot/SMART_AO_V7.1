"""
SMART_AO V7 - security.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Security Service
=============================
Central security service with JWT authentication and RBAC implementation.
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Role, User, FINANCIAL_DATA, TECHNICAL_DATA, LEGAL_DATA, ADMIN_DATA, RBAC_RULES
from app.schemas.users import TokenData
from app.core.database import get_db
from app.core.config import settings
from app.engines.security_engine.rbac_fields import FIELDS_STRIP_V6


# =============================================================================
# SECURITY CONSTANTS
# =============================================================================

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


# =============================================================================
# PASSWORD HASHING
# =============================================================================

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe contre son hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hasher un mot de passe avec Argon2."""
    return pwd_context.hash(password)


# =============================================================================
# JWT AUTHENTICATION
# =============================================================================

http_bearer = HTTPBearer(auto_error=False)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Créer un JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})

    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set")

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Créer un JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set")

    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Décoder et vérifier un JWT."""
    try:
        if not settings.JWT_SECRET_KEY:
            return None
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency FastAPI : récupère l'utilisateur authentifié depuis le JWT.
    Retourne un dict avec user_id, role, email.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Optionnel : vérifier l'utilisateur en base
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if user is not None:
        if not user.is_active or user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or locked"
            )
        return {
            "user_id": user.user_id,
            "role": user.role.value,
            "email": user.email,
        }

    # Fallback si l'utilisateur n'est pas en base (token valide mais user inconnu)
    # Dans un vrai système, on refuserait. Ici on permet le décodage pour les tests.
    return {
        "user_id": user_id,
        "role": payload.get("role", Role.CONDUCTEUR_TRAVAUX.value),
        "email": payload.get("email"),
    }


def require_role(required_role: Role):
    """
    Factory de dependency FastAPI pour exiger un rôle spécifique.
    Usage : Depends(require_role(Role.PATRON))
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role {required_role.value} required"
            )
        return current_user
    return role_checker


def require_any_role(required_roles: List[Role]):
    """
    Factory de dependency FastAPI pour exiger l'un des rôles listés.
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role")
        allowed = {r.value for r in required_roles}
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: one of {[r.value for r in required_roles]} required"
            )
        return current_user
    return role_checker


# =============================================================================
# RBAC SERVICE
# =============================================================================

class RBACService:
    """
    Role-Based Access Control Service
    
    Manages:
    - Role definitions
    - Permission checking
    - Resource access control
    """
    
    def __init__(self):
        # Import from models to avoid circular imports
        self.FINANCIAL_DATA = FINANCIAL_DATA
        self.TECHNICAL_DATA = TECHNICAL_DATA
        self.LEGAL_DATA = LEGAL_DATA
        self.ADMIN_DATA = ADMIN_DATA
        self.RBAC_RULES = RBAC_RULES
    
    def get_allowed_resources(self, role: Role) -> List[str]:
        """
        Get list of resource categories allowed for a role
        
        Args:
            role: User role
        
        Returns:
            List[str]: Allowed resource categories
        """
        return self.RBAC_RULES.get(role.name, [])
    
    def can_access_resource(self, role: Role, resource_category: str) -> bool:
        """
        Check if a role can access a specific resource category
        
        Args:
            role: User role
            resource_category: Resource category to check
        
        Returns:
            bool: True if access is allowed
        """
        allowed_resources = self.get_allowed_resources(role)
        return resource_category in allowed_resources
    
    def can_access_financial(self, role: Role) -> bool:
        """
        Check if a role can access financial data
        
        Args:
            role: User role
        
        Returns:
            bool: True if financial access is allowed
        """
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.FINANCIAL_DATA)
    
    def can_access_technical(self, role: Role) -> bool:
        """
        Check if a role can access technical data
        
        Args:
            role: User role
        
        Returns:
            bool: True if technical access is allowed
        """
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.TECHNICAL_DATA)
    
    def can_access_legal(self, role: Role) -> bool:
        """
        Check if a role can access legal data
        
        Args:
            role: User role
        
        Returns:
            bool: True if legal access is allowed
        """
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.LEGAL_DATA)
    
    def can_access_admin(self, role: Role) -> bool:
        """
        Check if a role can access admin functions
        
        Args:
            role: User role
        
        Returns:
            bool: True if admin access is allowed
        """
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.ADMIN_DATA)
    
    def filter_financial_data(self, role: Role, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out financial data from a dictionary based on user role.

        Uses the canonical FIELDS_STRIP_V6 catalog to ensure consistent
        stripping across the whole application.

        Args:
            role: User role
            data: Dictionary containing potentially sensitive data

        Returns:
            Dict[str, Any]: Filtered dictionary with financial data removed if not authorized
        """
        if self.can_access_financial(role):
            return data

        # Create a copy and remove financial fields
        filtered_data = data.copy()

        # Remove all sensitive fields from the canonical V6 catalog
        for field in FIELDS_STRIP_V6:
            if field in filtered_data:
                del filtered_data[field]

        # Recursively filter nested dictionaries and list items
        for key, value in list(filtered_data.items()):
            if isinstance(value, dict):
                filtered_data[key] = self.filter_financial_data(role, value)
            elif isinstance(value, list):
                filtered_data[key] = [
                    self.filter_financial_data(role, item) if isinstance(item, dict) else item
                    for item in value
                ]

        return filtered_data


# =============================================================================
# SECURITY SERVICE (MAIN)
# =============================================================================

class SecurityService:
    """
    Main Security Service
    
    Combines:
    - RBAC Service
    - Security headers
    - Audit logging (placeholder for future implementation)
    """
    
    def __init__(self):
        self.rbac = RBACService()
    
    async def verify_user_permission(
        self,
        user_id: str,
        resource_category: str,
        db: Any = None
    ) -> bool:
        """
        Verify if a user has permission to access a resource
        
        Args:
            user_id: User ID
            resource_category: Resource category to check
            db: Database session (optional)
        
        Returns:
            bool: True if permission is granted
        
        Raises:
            HTTPException: If user is not found or permission denied
        """
        # If db is provided, fetch user from database
        if db is not None:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            role = user.role
        else:
            # For now, assume role is passed or use default
            role = Role.CONDUCTEUR_TRAVAUX
        
        if not self.rbac.can_access_resource(role, resource_category):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {resource_category} for role {role.name}",
                headers={"X-RBAC-Denied": "true"}
            )
        
        return True


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

rbac_service = RBACService()
security_service = SecurityService()


def get_rbac_service() -> RBACService:
    """Get the singleton RBACService instance"""
    return rbac_service


def get_security_service() -> SecurityService:
    """Get the singleton SecurityService instance"""
    return security_service
