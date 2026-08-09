"""
SMART_AO V7 - rbac_strip.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - RBAC Financial Strip Middleware
=============================================
Middleware global qui supprime les champs financiers / stratégiques des
réponses JSON pour les rôles non autorisés.

Source: ARCHITECTURE_V7_ENGINE.md §4.2 + ADR-046
"""

import json
import logging
from typing import Any, Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.auth import decode_token
from app.models.user import Role
from app.engines.security_engine.rbac_fields import FIELDS_STRIP

logger = logging.getLogger(__name__)


def _strip_financial_data(data: Any) -> Any:
    """
    Supprime récursivement les champs sensibles d'une structure de données.
    """
    if isinstance(data, dict):
        filtered = {}
        for key, value in data.items():
            if key.lower() in FIELDS_STRIP:
                continue
            filtered[key] = _strip_financial_data(value)
        return filtered
    if isinstance(data, list):
        return [_strip_financial_data(item) for item in data]
    return data


def _role_can_access_financial(role_value: str) -> bool:
    """Détermine si un rôle (valeur ou nom) peut voir les données financières."""
    try:
        role = Role(role_value)
    except ValueError:
        try:
            role = Role[role_value.upper()]
        except KeyError:
            return False

    # Seul le PATRON (et rôles futurs avec accès financier) peut voir les €
    allowed = {Role.PATRON}
    return role in allowed


class RBACFinancialStripMiddleware(BaseHTTPMiddleware):
    """
    Middleware de strip financier global.

    - Décode le JWT de la requête pour extraire le rôle.
    - Si le rôle n'est pas autorisé aux données financières, filtre les
      réponses JSON avant de les renvoyer.
    - En cas d'erreur de filtrage, la réponse originale est conservée
      (fail-open sur le filtrage, fail-close sur l'accès qui reste géré
      par les endpoints).
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Ne filtrer que les réponses JSON
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # Extraire le rôle depuis le JWT
        role_value = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload:
                role_value = payload.get("role")

        # Si rôle inconnu ou non autorisé aux données financières, stripper
        if role_value is None or not _role_can_access_financial(role_value):
            try:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                if not body:
                    return response

                data = json.loads(body.decode("utf-8"))
                stripped = _strip_financial_data(data)
                new_body = json.dumps(stripped, ensure_ascii=False).encode("utf-8")

                new_headers = dict(response.headers)
                new_headers["Content-Length"] = str(len(new_body))
                new_headers["X-RBAC-Strip"] = "true"

                return Response(
                    content=new_body,
                    status_code=response.status_code,
                    headers=new_headers,
                    media_type="application/json",
                )
            except Exception as exc:
                logger.exception(f"RBAC strip middleware failure - fail-close applied")
                # FAIL-CLOSE : sur erreur interne, on refuse l'accès plutôt que de fuiter des données
                from starlette.responses import JSONResponse
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal authorization error - accès refusé par sécurité"}
                )

        return response
