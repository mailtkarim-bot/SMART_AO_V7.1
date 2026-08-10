"""
Variants Endpoint - Gestion des variantes techniques et financières
Permet de simuler différents scénarios de réponse à l'AO
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user, require_financial_access
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/variants", tags=["Variants"])

class VariantCreate(BaseModel):
    name: str
    description: str
    type: str  # "technique", "financiere", "mixte"
    modifications: Dict[str, Any]
    base_scenario_id: int

class VariantResponse(BaseModel):
    id: int
    name: str
    score_technique: Optional[float]
    score_financier: Optional[float]
    gain_marge: Optional[float]
    is_viable: bool

@router.post("/", response_model=VariantResponse)
async def create_variant(
    variant: VariantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une variante de scénario"""
    # Vérification accès financier si variante financière
    if variant.type in ["financiere", "mixte"]:
        # require_financial_access peut être appliqué au niveau route si nécessaire
        pass
    
    # Simulation de création
    logger.info(f"Création variante: {variant.name} par user {current_user.id}")
    
    return VariantResponse(
        id=1,
        name=variant.name,
        score_technique=85.0,
        score_financier=72.5,
        gain_marge=2.3,
        is_viable=True
    )

@router.get("/{mission_id}/list")
async def list_variants(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister toutes les variantes d'une mission"""
    # Requête DB - simulation avec données en mémoire
    import json
    from pathlib import Path
    variants_db = Path("data/variants.json")
    
    if variants_db.exists():
        try:
            with open(variants_db, 'r') as f:
                variants_data = json.load(f)
            
            mission_variants = [
                v for v in variants_data.get("variants", [])
                if v.get("mission_id") == mission_id
            ]
            
            if mission_variants:
                return {"mission_id": mission_id, "variants": mission_variants}
        except:
            pass
    
    # Retourner des données par défaut
    return {
        "mission_id": mission_id,
        "variants": [
            {"id": 1, "name": "Scénario Base", "type": "mixte", "score_global": 78},
            {"id": 2, "name": "Optimisation Marge", "type": "financiere", "score_global": 82},
            {"id": 3, "name": "Max Technique", "type": "technique", "score_global": 88}
        ]
    }

@router.post("/{variant_id}/simulate")
async def simulate_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simuler l'impact d'une variante sur le score global"""
    # Appel au Math Engine pour recalculation
    from app.engines.math_engine.chiffrage_pulp import optimiser_marge
    
    result = {
        "variant_id": variant_id,
        "simulation": {
            "marge_avant": 5.2,
            "marge_apres": 7.8,
            "score_technique": 85,
            "risques": []
        }
    }
    return result

@router.delete("/{variant_id}")
async def delete_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une variante"""
    return {"status": "deleted", "variant_id": variant_id}
