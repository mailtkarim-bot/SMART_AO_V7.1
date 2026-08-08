"""
SMART_AO V7 - deps.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - API Gateway Dependencies
======================================
Définition des dépendances FastAPI pour l'API Gateway
Inclut l'authentification, le RBAC, et les services partagés

Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from app.models.user import Role, User, RBAC_RULES, FINANCIAL_DATA, TECHNICAL_DATA, LEGAL_DATA
from app.core.database import async_get_db
from app.core.security import RBACService, SecurityService
from app.core.config import settings
from jose import JWTError, jwt
from sqlalchemy import select

logger = logging.getLogger(__name__)


# =============================================================================
# SERVICE DE SÉCURITÉ
# =============================================================================

class SecurityDependencies:
    """
    Dépendances de sécurité pour l'API Gateway.
    """
    
    def __init__(self):
        self.security_token = HTTPBearer()
        self.rbac_service = RBACService()
        self.security_service = SecurityService()
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """
        Récupérer l'utilisateur courant à partir du token JWT.
        """
        try:
            token = credentials.credentials
            if not settings.JWT_SECRET_KEY:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWT secret key is not configured",
                )

            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id = payload.get("sub")
            role = payload.get("role", "sous_traitant")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return {
                "user_id": user_id,
                "role": role
            }
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def get_current_user_from_db(self, request: Request) -> User:
        """
        Récupérer l'utilisateur depuis la base de données.
        """
        db = await async_get_db()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        try:
            if not settings.JWT_SECRET_KEY:
                raise HTTPException(status_code=500, detail="JWT secret key is not configured")

            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid user")
            
            result = await db.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return user
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def verify_financial_access(self, current_user: Dict[str, Any]) -> bool:
        """
        Vérifier que l'utilisateur a accès aux données financières.
        """
        role = current_user.get("role", "sous_traitant")
        
        try:
            user_role = Role[role.upper()]
            allowed = self.rbac_service.can_access_financial(user_role)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès interdit aux données financières"
                )
            
            return True
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle utilisateur invalide"
            )
    
    async def verify_technical_access(self, current_user: Dict[str, Any]) -> bool:
        """
        Vérifier que l'utilisateur a accès aux données techniques.
        """
        role = current_user.get("role", "sous_traitant")
        
        try:
            user_role = Role[role.upper()]
            allowed = self.rbac_service.can_access_technical(user_role)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès interdit aux données techniques"
                )
            
            return True
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle utilisateur invalide"
            )
    
    async def verify_admin_access(self, current_user: Dict[str, Any]) -> bool:
        """
        Vérifier que l'utilisateur a accès aux fonctions d'administration.
        """
        role = current_user.get("role", "sous_traitant")
        
        try:
            user_role = Role[role.upper()]
            allowed = self.rbac_service.can_access_admin(user_role)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accès administrateur requis"
                )
            
            return True
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rôle utilisateur invalide"
            )


# =============================================================================
# DÉPENDANCES DE RATE LIMITING
# =============================================================================

class RateLimitDependencies:
    """
    Dépendances pour le rate limiting.
    """
    
    def __init__(self):
        self.request_counts: Dict[str, int] = {}
    
    async def check_rate_limit(self, request: Request) -> bool:
        """
        Vérifier le rate limiting pour une requête.
        """
        client_ip = request.client.host
        
        # Implémentation simplifiée - à remplacer par Redis
        count = self.request_counts.get(client_ip, 0)
        
        if count >= 100:  # Limite à 100 requêtes
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
        
        self.request_counts[client_ip] = count + 1
        return True


# =============================================================================
# DÉPENDANCES PRINCIPALES (EXPORT)
# =============================================================================

# Créer les instances
security_deps = SecurityDependencies()
rate_limit_deps = RateLimitDependencies()

# Dépendances exportées
get_current_user = security_deps.get_current_user
verify_financial_access = security_deps.verify_financial_access
verify_technical_access = security_deps.verify_technical_access
verify_admin_access = security_deps.verify_admin_access

check_rate_limit = rate_limit_deps.check_rate_limit


# =============================================================================
# FABRIQUE DE DÉPENDANCES
# =============================================================================

def create_dependencies():
    """
    Créer et retourner toutes les dépendances.
    """
    return {
        "security": security_deps,
        "rate_limit": rate_limit_deps
    }


if __name__ == "__main__":
    print("Dependencies module loaded")
    print(f"Security deps: {security_deps}")
    print(f"Rate limit deps: {rate_limit_deps}")

