"""
SMART_AO V7 - user.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - User Model
========================
PostgreSQL User model with RBAC support
Source: ARCHITECTURE_V7_ENGINE.md §4.2 + ADR-046
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


# =============================================================================
# ENUMS
# =============================================================================

class Role(Enum):
    """RBAC Roles for BTP Users - SSoT V7 Security Engine"""
    PATRON = "patron"                   # Accès complet (marges, coefficients, trésorerie)
    CONDUCTEUR_TRAVAUX = "conducteur_travaux"  # Accès limité (planning, qualité)
    CHARGE_ETUDES = "charge_etudes"    # Accès technique (CCTP, DPGF)
    RESPONSABLE_QSSE = "qsse"          # Sécurité, environnement
    SOUS_TRAITANT = "sous_traitant"    # Accès restreint (lots attribués)


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# =============================================================================
# RESOURCE CATEGORIES FOR RBAC
# =============================================================================

# Ressources protégées par RBAC
FINANCIAL_DATA = ["marge", "coefficient", "tresorerie", "bfr", "penalite", "prix", "cout", "chiffrage"]
TECHNICAL_DATA = ["cctp", "dpgf", "planning", "methodes", "metre", "etude"]
LEGAL_DATA = ["ccag", "ccmi", "contentieux", "assurance", "contrat", "clause"]
ADMIN_DATA = ["user_management", "system_config"]

# Matrice d'accès RBAC - Qui a accès à quoi
RBAC_RULES = {
    "patron": FINANCIAL_DATA + TECHNICAL_DATA + LEGAL_DATA + ADMIN_DATA,
    "conducteur_travaux": TECHNICAL_DATA + LEGAL_DATA,  # Pas de données financières
    "charge_etudes": TECHNICAL_DATA + LEGAL_DATA,  # Pas de données financières
    "qsse": LEGAL_DATA,  # Seulement sécurité et conformité
    "sous_traitant": [],  # Accès par mission seulement (filtré par mission_id)
}


# =============================================================================
# USER MODEL
# =============================================================================

class User(Base):
    """
    User model representing a system user with RBAC support
    
    Attributes:
        id: Unique identifier
        user_id: Human-readable user ID (UUID)
        email: User email (unique)
        username: User username (unique)
        full_name: Full name
        role: User role (RBAC)
        hashed_password: Hashed password
        is_active: Account status
        status: Detailed status
        email_verified: Email verification status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
        failed_login_attempts: Failed login attempts counter
        lock_until: Account lock timestamp (if suspended)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(128), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), default=Role.CONDUCTEUR_TRAVAUX, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    lock_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (si nécessaire pour les missions utilisateur)
    # missions = relationship("Mission", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, email={self.email}, role={self.role})>"
    
    @property
    def is_superuser(self) -> bool:
        """Check if user has admin privileges"""
        return self.role == Role.PATRON
    
    @property
    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.lock_until is None:
            return False
        return datetime.now(timezone.utc) < self.lock_until
    
    def can_access_resource(self, resource_category: str) -> bool:
        """
        Check if user can access a resource category based on RBAC rules
        
        Args:
            resource_category: Category of resource (FINANCIAL_DATA, TECHNICAL_DATA, etc.)
        
        Returns:
            bool: True if access is allowed
        """
        if not self.is_active or self.is_locked:
            return False
        
        allowed_resources = RBAC_RULES.get(self.role.name, [])
        return resource_category in allowed_resources
    
    def can_access_financial_data(self) -> bool:
        """Check if user can access financial data"""
        return self.can_access_resource("marge")  # "marge" est dans FINANCIAL_DATA
    
    def is_patron(self) -> bool:
        """Check if user is patron (full access)"""
        return self.role == Role.PATRON
    
    def is_sous_traitant(self) -> bool:
        """Check if user is sous-traitant (restricted access)"""
        return self.role == Role.SOUS_TRAITANT
