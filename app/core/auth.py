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
SMART_AO V7 - Authentication Service
====================================
JWT-based authentication service with password hashing
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User, Role, UserStatus
from app.schemas.users import TokenData, UserInDB


# =============================================================================
# PASSWORD HASHING
# =============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

class AuthService:
    """
    JWT Authentication Service
    
    Handles:
    - Access token creation
    - Refresh token creation
    - Token verification
    - Password management
    """
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(
        self, 
        subject: str, 
        expires_delta: Optional[timedelta] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            subject: User identifier (user_id)
            expires_delta: Custom expiration time
            extra_data: Additional claims to include in token
        
        Returns:
            str: Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "sub": subject,
            "type": "access"
        }
        
        if extra_data:
            to_encode.update(extra_data)
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        subject: str, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token
        
        Args:
            subject: User identifier (user_id)
            expires_delta: Custom expiration time
        
        Returns:
            str: Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)
        
        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode = {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "sub": subject,
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def decode_token(self, token: str) -> TokenData:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            TokenData: Decoded token payload
        
        Raises:
            JWTError: If token is invalid or expired
        """
        payload = jwt.decode(
            token, 
            self.secret_key, 
            algorithms=[self.algorithm]
        )
        
        token_data = TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            role=payload.get("role")
        )
        
        return token_data
    
    def verify_access_token(self, token: str) -> TokenData:
        """
        Verify an access token and return its data
        
        Args:
            token: JWT access token
        
        Returns:
            TokenData: Token payload data
        
        Raises:
            JWTError: If token is invalid or expired
        """
        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )
        
        # Verify token type
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        
        return TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            role=payload.get("role")
        )
    
    def create_tokens_for_user(self, user: UserInDB) -> Dict[str, str]:
        """
        Create both access and refresh tokens for a user
        
        Args:
            user: User database model
        
        Returns:
            Dict: Dictionary with access_token and refresh_token
        """
        # Prepare extra data for token
        extra_data = {
            "username": user.username,
            "email": user.email,
            "role": user.role.name
        }
        
        access_token = self.create_access_token(
            subject=user.user_id,
            extra_data=extra_data
        )
        
        refresh_token = self.create_refresh_token(
            subject=user.user_id
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }


# Singleton instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get the singleton AuthService instance"""
    return auth_service
