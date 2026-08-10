"""
SMART_AO V7 - main.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Application Principale
===================================
Point d'entrée FastAPI pour l'API REST V7.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1.endpoints import health, missions, agents, documents, workflows, enveloppes
from app.engines.api_gateway import finance, finance_advanced, rag
from app.engines.api_gateway import (
    alloti_guardian,
    certif_live_checker,
    deadline_guardian,
    workflow_delegate,
    users,
    qr_moe,
    dce_analyze_v6_compat,
    pab_detector,
    post_gagne_tracker,
    memoire_booster
)
from app.api.v1.endpoints import dce_analyze, dce_analyze_v7, handoff, pricing, reports, variants, missions_v7
from app.api.middleware.rate_limiting import setup_rate_limiting, limiter
from app.api.middleware.rbac_strip import RBACFinancialStripMiddleware
from app.core.resilience import reset_all_circuit_breakers

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Lifespan context manager pour FastAPI (remplace on_event déprécié)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 SMART_AO V7 API started successfully")
    logger.info(f"   Docs: http://{settings.API_HOST}:{settings.API_PORT}/api/docs")
    logger.info(f"   Redoc: http://{settings.API_HOST}:{settings.API_PORT}/api/redoc")
    
    # Initialiser le rate limiting
    setup_rate_limiting(app, enabled=not settings.DEBUG)
    if settings.DEBUG:
        logger.info("⚠️  Rate limiting DÉSACTIVÉ (mode debug)")
    
    # Reset des circuit breakers au démarrage (utile pour dev)
    reset_all_circuit_breakers()
    
    yield
    # Shutdown
    logger.info("🛑 SMART_AO V7 API shutting down")


# Créer l'application
app = FastAPI(
    title="SMART_AO V7 Engine OS",
    description="API REST pour le système SMART_AO V7 - Gestion des appels d'offres BTP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    # Websockets activés pour les notifications temps réel
    disable_websockets=False,
    lifespan=lifespan,
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Middleware RBAC : strip financier global pour les rôles non autorisés
app.add_middleware(RBACFinancialStripMiddleware)

# Middleware Audit Trail : traçabilité des accès financiers
from app.api.middleware.audit_trail import AuditTrailMiddleware
app.add_middleware(AuditTrailMiddleware)

# Inclure les routers
app.include_router(health.router)
app.include_router(missions.router)
app.include_router(agents.router)
app.include_router(documents.router)
app.include_router(workflows.router)
app.include_router(enveloppes.router)
app.include_router(finance.router)
app.include_router(finance_advanced.router)
app.include_router(rag.router)

# P0 API Gateway Endpoints - mounted
app.include_router(alloti_guardian.router)
app.include_router(certif_live_checker.router)
app.include_router(deadline_guardian.router)
app.include_router(workflow_delegate.router)
app.include_router(users.router)
app.include_router(qr_moe.router)
app.include_router(dce_analyze_v6_compat.router)
app.include_router(pab_detector.router)
app.include_router(post_gagne_tracker.router)
app.include_router(memoire_booster.router)

# Monter les endpoints supplémentaires
app.include_router(dce_analyze.router)
app.include_router(dce_analyze_v7.router)
app.include_router(handoff.router)
app.include_router(pricing.router)
app.include_router(reports.router)
app.include_router(variants.router)
app.include_router(missions_v7.router)

# Ajouter l'état limiter à l'app pour les endpoints
app.state.limiter = limiter


# Les événements startup/shutdown sont gérés par lifespan ci-dessus

# Pour le démarrage direct
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )

