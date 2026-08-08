"""
SMART_AO V7 - response.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class ErrorResponse(BaseModel):
    '''Schema de réponse pour les erreurs.'''
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    '''Schema de réponse pour les succès.'''
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Dict[str, Any]] = None
