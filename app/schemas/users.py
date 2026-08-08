"""
SMART_AO V7 - users.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - User Schemas
==========================
Pydantic schemas for User model (request/response validation)
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# =============================================================================
# ENUMS
# =============================================================================

class Role(str, Enum):
    """RBAC Roles for BTP Users"""
    PATRON = "patron"
    CONDUCTEUR_TRAVAUX = "conducteur_travaux"
    CHARGE_ETUDES = "charge_etudes"
    RESPONSABLE_QSSE = "qsse"
    SOUS_TRAITANT = "sous_traitant"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# =============================================================================
# USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=128, description="User username")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: Role = Field(default=Role.CONDUCTEUR_TRAVAUX, description="User role (RBAC)")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="User password (will be hashed)")
    
    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(default=None, description="User email address")
    username: Optional[str] = Field(default=None, min_length=3, max_length=128, description="User username")
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Full name")
    role: Optional[Role] = Field(default=None, description="User role (RBAC)")
    is_active: Optional[bool] = Field(default=None, description="Account status")
    status: Optional[UserStatus] = Field(default=None, description="Detailed status")
    
    model_config = ConfigDict(extra="forbid")


class UserInDBBase(UserBase):
    """Base schema for user in database (includes ID)"""
    user_id: str = Field(..., description="Human-readable user ID")
    is_active: bool = Field(default=True, description="Account status")
    status: UserStatus = Field(default=UserStatus.PENDING, description="Detailed status")
    email_verified: bool = Field(default=False, description="Email verification status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")


class UserInDB(UserInDBBase):
    """Full user schema from database (internal use)"""
    id: int = Field(..., description="Database ID")
    hashed_password: str = Field(..., description="Hashed password")
    failed_login_attempts: int = Field(default=0, description="Failed login attempts counter")
    lock_until: Optional[datetime] = Field(default=None, description="Account lock timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserInDBBase):
    """Public user schema (excludes sensitive data)"""
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Response schema for listing users"""
    users: List[UserPublic] = Field(default_factory=list, description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class Token(BaseModel):
    """JWT Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserPublic = Field(..., description="User information")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = Field(default=None, description="User ID")
    username: Optional[str] = Field(default=None, description="Username")
    email: Optional[str] = Field(default=None, description="Email")
    role: Optional[Role] = Field(default=None, description="User role")


class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=8, description="Password")
    
    model_config = ConfigDict(extra="forbid")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")
    
    model_config = ConfigDict(extra="forbid")


# =============================================================================
# RBAC PERMISSION SCHEMAS
# =============================================================================

class PermissionCheck(BaseModel):
    """Schema for checking user permissions"""
    resource: str = Field(..., description="Resource to check access for")
    action: str = Field(..., description="Action to perform (read, write, delete, etc.)")
    
    model_config = ConfigDict(extra="forbid")


class PermissionResponse(BaseModel):
    """Response for permission check"""
    resource: str = Field(..., description="Resource checked")
    action: str = Field(..., description="Action checked")
    allowed: bool = Field(..., description="Whether access is allowed")
    reason: Optional[str] = Field(default=None, description="Reason if denied")


class UserPermissionsResponse(BaseModel):
    """Response for user permissions"""
    user_id: str = Field(..., description="User ID")
    role: Role = Field(..., description="User role")
    allowed_resources: List[str] = Field(default_factory=list, description="List of allowed resource categories")
    can_access_financial: bool = Field(..., description="Can access financial data")
    can_access_technical: bool = Field(..., description="Can access technical data")
    can_access_legal: bool = Field(..., description="Can access legal data")
    can_access_admin: bool = Field(..., description="Can access admin functions")
