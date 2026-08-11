"""
SMART_AO V7 - rbac.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - RBAC Engine
==========================
Role-Based Access Control enforcement for agents and resources
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from typing import Optional, List, Dict, Any, Callable
from fastapi import Depends, HTTPException, status

from app.models.user import Role, User, FINANCIAL_DATA, TECHNICAL_DATA, LEGAL_DATA, ADMIN_DATA, RBAC_RULES
from app.schemas.users import TokenData
from app.core.auth import get_rbac_service, get_security_service, get_current_user
from app.core.database import get_db as async_get_db
from app.agents.base_agent import AgentOutput
from app.engines.security_engine.rbac_fields import FIELDS_STRIP_V6, is_sensitive_field


# =============================================================================
# RBAC ENFORCER
# =============================================================================

class RBACEnforcer:
    """
    RBAC Enforcer for SMART_AO V7
    
    Enforces access control on:
    - Agent outputs (filter financial_data based on role)
    - API endpoints (check permissions)
    - Document access (verify tenant isolation)
    """
    
    def __init__(self):
        self.rbac_service = get_rbac_service()
        self.security_service = get_security_service()
    
    def filter_agent_output_by_role(self, agent_output: AgentOutput, role: Role) -> AgentOutput:
        """
        Filter agent output based on user role
        
        Removes financial_data if user doesn't have financial access
        
        Args:
            agent_output: Agent output to filter
            role: User role
        
        Returns:
            AgentOutput: Filtered agent output
        """
        # Check if user can access financial data
        can_access_financial = self.rbac_service.can_access_financial(role)
        
        # If user cannot access financial data, remove it from output
        if not can_access_financial and agent_output.financial_data is not None:
            agent_output.financial_data = None
        
        return agent_output
    
    def filter_mission_data_by_role(self, mission_data: Dict[str, Any], role: Role) -> Dict[str, Any]:
        """
        Filter mission data based on user role
        
        Removes financial fields if user doesn't have financial access
        
        Args:
            mission_data: Mission data dictionary
            role: User role
        
        Returns:
            Dict[str, Any]: Filtered mission data
        """
        if self.rbac_service.can_access_financial(role):
            return mission_data
        
        # Create a copy to avoid modifying original
        filtered_data = mission_data.copy()

        # Remove all sensitive fields defined in the canonical V6 catalog
        for field in FIELDS_STRIP_V6:
            if field in filtered_data:
                del filtered_data[field]

        # Recursively filter nested dictionaries
        for key, value in list(filtered_data.items()):
            if isinstance(value, dict):
                filtered_data[key] = self.filter_mission_data_by_role(value, role)
            elif isinstance(value, list):
                filtered_data[key] = [
                    self.filter_mission_data_by_role(item, role) if isinstance(item, dict) else item
                    for item in value
                ]

        return filtered_data
    
    async def verify_agent_access(
        self,
        agent_name: str,
        role: Role,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Verify if a user with given role can access an agent
        
        Args:
            agent_name: Name of the agent
            role: User role
            tags: Agent tags (optional)
        
        Returns:
            bool: True if access is allowed
        
        Raises:
            HTTPException: If access is denied
        """
        # Check if agent has admin_only tag
        if tags and "admin_only" in tags:
            if not self.rbac_service.can_access_admin(role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Agent {agent_name} requires admin privileges",
                    headers={"X-RBAC-Denied": "true"}
                )
        
        # Check if agent has finance tag
        if tags and "finance" in tags:
            if not self.rbac_service.can_access_financial(role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: Agent {agent_name} contains financial data",
                    headers={"X-RBAC-Denied": "true"}
                )
        
        return True
    
    async def create_rbac_dependency(
        self,
        resource_category: str,
        action: str = "read"
    ) -> Callable:
        """
        Factory to create RBAC dependency for FastAPI endpoints
        
        Args:
            resource_category: Resource category to check
            action: Action to perform
        
        Returns:
            Callable: FastAPI dependency function
        """
        async def dependency(
            current_user: TokenData = Depends(get_current_user)
        ) -> TokenData:
            """Dependency function that checks RBAC permissions"""
            # Convert string role to Role enum
            try:
                role = Role[current_user.role]
            except KeyError:
                role = Role.CONDUCTEUR_TRAVAUX
            
            if not self.rbac_service.can_access_resource(role, resource_category):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to {resource_category} for role {role.name}",
                    headers={"X-RBAC-Denied": "true"}
                )
            
            return current_user
        
        return dependency


# =============================================================================
# SINGLETON INSTANCE
# ==============================================================================

rbac_enforcer = RBACEnforcer()


def get_rbac_enforcer() -> RBACEnforcer:
    """Get the singleton RBACEnforcer instance"""
    return rbac_enforcer
