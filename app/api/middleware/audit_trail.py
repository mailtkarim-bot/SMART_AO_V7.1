"""
SMART_AO V7 - audit_trail.py
================================
Middleware d'audit pour tracer tous les accès aux endpoints financiers sensibles.

Ce middleware enregistre:
1. Qui a accédé à quelle ressource financière
2. Quand l'accès a eu lieu
3. Le résultat de la requête (succès/échec)
4. L'adresse IP et le user agent

Intégration avec:
- require_financial_access pour logging automatique
- Système de logs structuré JSON
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("audit_trail")


class AuditTrailMiddleware(BaseHTTPMiddleware):
    """Middleware pour l'audit des accès financiers."""
    
    async def dispatch(self, request: Request, call_next):
        # Vérifier si c'est un endpoint financier sensible
        financial_paths = [
            "/api/v1/finance",
            "/api/v1/finance/advanced",
            "/api/v1/enveloppes",
            "/api/v1/rag",
        ]
        
        is_financial_endpoint = any(
            request.url.path.startswith(path) 
            for path in financial_paths
        )
        
        if not is_financial_endpoint:
            # Passer directement pour les endpoints non-financiers
            return await call_next(request)
        
        # Enregistrer le début de la requête
        start_time = datetime.now()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Tenter d'extraire l'utilisateur (sera fait proprement après auth)
        user_id = "anonymous"
        user_role = "unknown"
        
        try:
            # Exécuter la requête
            response = await call_next(request)
            
            # Extraire les infos utilisateur du state si disponible
            if hasattr(request.state, "current_user"):
                user_data = request.state.current_user
                user_id = user_data.get("user_id", user_data.get("sub", "unknown"))
                user_role = user_data.get("role", "unknown")
            
            # Calculer le temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log d'audit structuré
            audit_log = {
                "timestamp": start_time.isoformat(),
                "event_type": "FINANCIAL_ACCESS",
                "user_id": user_id,
                "user_role": user_role,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "processing_time_ms": round(processing_time, 2),
                "access_granted": response.status_code != 403,
            }
            
            # Logger l'événement
            if response.status_code == 403:
                logger.warning(f"AUDIT ACCES REFUSE: {json.dumps(audit_log)}")
            else:
                logger.info(f"AUDIT ACCES AUTORISE: {json.dumps(audit_log)}")
            
            # Ajouter les headers d'audit à la réponse
            response.headers["X-Audit-Logged"] = "true"
            response.headers["X-Audit-Timestamp"] = start_time.isoformat()
            
            return response
            
        except Exception as e:
            # Logguer les erreurs aussi
            error_log = {
                "timestamp": start_time.isoformat(),
                "event_type": "FINANCIAL_ACCESS_ERROR",
                "user_id": user_id,
                "path": request.url.path,
                "method": request.method,
                "error": str(e),
                "client_ip": client_ip,
            }
            logger.error(f"AUDIT ERREUR: {json.dumps(error_log)}")
            raise


# Fonction utilitaire pour log manuel dans les endpoints
def log_financial_access(
    user_id: str,
    user_role: str,
    action: str,
    resource: str,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None
):
    """
    Fonction utilitaire pour logguer manuellement un accès financier.
    
    Args:
        user_id: ID de l'utilisateur
        user_role: Rôle de l'utilisateur
        action: Action effectuée (READ, WRITE, DELETE, EXPORT)
        resource: Ressource accédée
        success: Si l'action a réussi
        details: Détails supplémentaires
    """
    audit_log = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "FINANCIAL_ACCESS_MANUAL",
        "user_id": user_id,
        "user_role": user_role,
        "action": action,
        "resource": resource,
        "success": success,
        "details": details or {}
    }
    
    if success:
        logger.info(f"AUDIT MANUAL: {json.dumps(audit_log)}")
    else:
        logger.warning(f"AUDIT MANUAL ECHEC: {json.dumps(audit_log)}")
