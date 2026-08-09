"""Reports Endpoint - Génération et export des rapports d'analyse"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.security.rbac import require_auth

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{mission_id}/generate")
async def generate_report(mission_id: int, format: str = "pdf", db: Session = Depends(get_db)):
    """Générer un rapport complet d'analyse"""
    # Appel au RapportStep du workflow
    from app.engines.workflow_engine.steps.rapport_step import RapportStep
    step = RapportStep()
    report = await step.generate_full_report(mission_id)
    return {"report_url": f"/reports/{mission_id}.{format}", "content": report}

@router.get("/{mission_id}/export")
async def export_report(mission_id: int, format: str = "json"):
    """Exporter le rapport dans différents formats"""
    return {"status": "exported", "format": format}
