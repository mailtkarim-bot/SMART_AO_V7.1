"""
SMART_AO V7 - API Gateway __init__.py
======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

API Gateway - Passerelle API pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from app.engines.api_gateway.workflow_delegate import *
from app.engines.api_gateway.users import *
from app.engines.api_gateway.qr_moe import *
from app.engines.api_gateway.pab_detector import *
from app.engines.api_gateway.post_gagne_tracker import *
from app.engines.api_gateway.memoire_booster import *
from app.engines.api_gateway.dce_analyze_v6_compat import *
from app.engines.api_gateway.deadline_guardian import *
from app.engines.api_gateway.alloti_guardian import *
from app.engines.api_gateway.certif_live_checker import *
from app.engines.api_gateway.contentieux_generator import *
from app.engines.api_gateway.handoff_plus import *

__all__ = [
    # Modules API Gateway
    'workflow_delegate', 'users', 'qr_moe', 'pab_detector',
    'post_gagne_tracker', 'memoire_booster', 'dce_analyze_v6_compat',
    'deadline_guardian', 'alloti_guardian', 'certif_live_checker',
    'contentieux_generator', 'handoff_plus',
    # Routers
    'router as workflow_delegate_router',
    'router as users_router',
    'router as qr_moe_router',
    'router as pab_detector_router',
    'router as post_gagne_tracker_router',
    'router as memoire_booster_router',
    'router as dce_analyze_v6_compat_router',
    'router as deadline_guardian_router',
    'router as alloti_guardian_router',
    'router as certif_live_checker_router',
    'router as contentieux_generator_router',
    'router as handoff_plus_router'
]

def get_all_routers():
    """Retourne tous les routers de l'API Gateway."""
    from fastapi import APIRouter
    routers = []
    
    try:
        from app.engines.api_gateway.workflow_delegate import router as wf_router
        routers.append(("/api/v7/workflow", wf_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.users import router as users_router
        routers.append(("/api/v7/users", users_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.qr_moe import router as qr_router
        routers.append(("/api/v7/qr-moe", qr_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.pab_detector import router as pab_router
        routers.append(("/api/v7/pab", pab_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.post_gagne_tracker import router as pg_router
        routers.append(("/api/v7/post-gagne", pg_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.memoire_booster import router as mb_router
        routers.append(("/api/v7/memoire", mb_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.dce_analyze_v6_compat import router as dce_router
        routers.append(("/api/v7/dce", dce_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.deadline_guardian import router as dl_router
        routers.append(("/api/v7/deadlines", dl_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.alloti_guardian import router as ag_router
        routers.append(("/api/v7/alloti", ag_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.certif_live_checker import router as certif_router
        routers.append(("/api/v7/certif", certif_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.contentieux_generator import router as cont_router
        routers.append(("/api/v7/contentieux", cont_router))
    except ImportError as e:
        pass
    
    try:
        from app.engines.api_gateway.handoff_plus import router as hf_router
        routers.append(("/api/v7/handoff", hf_router))
    except ImportError as e:
        pass
    
    return routers


def mount_all_routers(main_app):
    """Monte tous les routers sur l'application principale."""
    for prefix, router in get_all_routers():
        main_app.include_router(router, prefix=prefix)
    return main_app

