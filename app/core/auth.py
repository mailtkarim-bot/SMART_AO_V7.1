"""
SMART_AO V7 - Authentication & Authorization Module (SSoT)
======================================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Unified authentication module - Single Source of Truth
- Argon2 password hashing
- JWT token management
- RBAC enforcement
- Single get_current_user dependency

Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Role, FINANCIAL_DATA, TECHNICAL_DATA, LEGAL_DATA, ADMIN_DATA, RBAC_RULES
from app.schemas.users import TokenData
from app.core.database import get_db
from app.core.config import settings
from app.engines.security_engine.rbac_fields import FIELDS_STRIP_V6


# =============================================================================
# SECURITY CONSTANTS
# =============================================================================

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


# =============================================================================
# PASSWORD HASHING (Argon2 - SSoT)
# =============================================================================

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Argon2."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with Argon2."""
    return pwd_context.hash(password)


# =============================================================================
# JWT AUTHENTICATION (SSoT)
# =============================================================================

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={})


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
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
    """Create a JWT refresh token."""
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
    """Decode and verify a JWT token."""
    try:
        if not settings.JWT_SECRET_KEY:
            return None
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# =============================================================================
# CURRENT USER DEPENDENCY (SSoT - Returns TokenData, NO FALLBACK)
# =============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """
    SSoT Dependency: Get the current authenticated user from JWT.
    
    Returns TokenData (not dict) for consistency across all endpoints.
    NO FALLBACK - Fail-close if user not found or inactive (P0-2 FIX).
    
    Raises:
        HTTPException 401: Invalid/expired token or user not found
        HTTPException 403: User inactive or locked
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

    # MANDATORY: Verify user exists in database - NO FALLBACK (P0-2 FIX)
    result = await db.execute(select(User).where(User.user_id == user_id))
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
            detail="User account is inactive"
        )

    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is locked"
        )

    # Return TokenData for consistency (not dict)
    return TokenData(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role.value
    )


# =============================================================================
# ROLE-BASED DEPENDENCIES
# =============================================================================

def require_role(required_role: Role) -> Callable:
    """Factory dependency to require a specific role."""
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        user_role = current_user.role
        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: role {required_role.value} required"
            )
        return current_user
    return role_checker


def require_any_role(required_roles: List[Role]) -> Callable:
    """Factory dependency to require any of the listed roles."""
    def role_checker(current_user: TokenData = Depends(get_current_user)):
        user_role = current_user.role
        allowed = {r.value for r in required_roles}
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: one of {[r.value for r in required_roles]} required"
            )
        return current_user
    return role_checker


# =============================================================================
# RBAC SERVICE (SSoT)
# =============================================================================

class RBACService:
    """Role-Based Access Control Service - SSoT"""
    
    def __init__(self):
        self.FINANCIAL_DATA = FINANCIAL_DATA
        self.TECHNICAL_DATA = TECHNICAL_DATA
        self.LEGAL_DATA = LEGAL_DATA
        self.ADMIN_DATA = ADMIN_DATA
        self.RBAC_RULES = RBAC_RULES
    
    def get_allowed_resources(self, role: Role) -> List[str]:
        """Get list of resource categories allowed for a role."""
        return self.RBAC_RULES.get(role.name, [])
    
    def can_access_resource(self, role: Role, resource_category: str) -> bool:
        """Check if a role can access a specific resource category."""
        allowed_resources = self.get_allowed_resources(role)
        return resource_category in allowed_resources
    
    def can_access_financial(self, role: Role) -> bool:
        """Check if a role can access financial data."""
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.FINANCIAL_DATA)
    
    def can_access_technical(self, role: Role) -> bool:
        """Check if a role can access technical data."""
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.TECHNICAL_DATA)
    
    def can_access_legal(self, role: Role) -> bool:
        """Check if a role can access legal data."""
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.LEGAL_DATA)
    
    def can_access_admin(self, role: Role) -> bool:
        """Check if a role can access admin functions."""
        allowed_resources = self.get_allowed_resources(role)
        return any(resource in allowed_resources for resource in self.ADMIN_DATA)
    
    def filter_financial_data(self, role: Role, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out financial data from a dictionary based on user role."""
        if self.can_access_financial(role):
            return data
        
        filtered_data = data.copy()
        for field in FIELDS_STRIP_V6:
            if field in filtered_data:
                del filtered_data[field]
        
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
# FINANCIAL ACCESS DEPENDENCY (Moved from middleware/auth.py - SSoT)
# =============================================================================

async def require_financial_access(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency that requires financial data access permission.
    Only PATRON can access financial data.
    Uses get_current_user from SSoT (this module).
    """
    user_role = current_user.role
    allowed_resources = RBAC_RULES.get(user_role, [])
    
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
    """Dependency that requires admin access. Only PATRON can access admin functions."""
    if current_user.role != "patron":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin functions require PATRON role",
            headers={"X-RBAC-Denied": "true"},
        )
    
    return current_user


# =============================================================================
# SECURITY SERVICE
# =============================================================================

class SecurityService:
    """Main Security Service"""
    
    def __init__(self):
        self.rbac = RBACService()
    
    async def verify_user_permission(
        self,
        user_id: str,
        resource_category: str,
        db: Any = None
    ) -> bool:
        """Verify if a user has permission to access a resource."""
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


# =============================================================================
# RESOURCE ACCESS CHECK FACTORY
# =============================================================================

def check_resource_access(resource_category: str, action: str = "read") -> Callable:
    """Factory function to create permission check dependencies."""
    async def dependency(
        current_user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        """Check if current user has permission to access the resource."""
        user_role = current_user.role
        allowed_resources = RBAC_RULES.get(user_role, [])
        
        if resource_category not in allowed_resources:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {resource_category}. Role {user_role} not authorized.",
                headers={"X-RBAC-Denied": "true"},
            )
        
        return current_user
    
    return dependency
