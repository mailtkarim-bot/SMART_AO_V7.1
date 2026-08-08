"""
SMART_AO V7 - finance.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Finance API Gateway
=================================
Endpoint et services financiers pour l'API Gateway
Intègre les calculs du Math Engine avec le RBAC

Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from app.models.user import Role
from app.core.security import get_current_user, get_rbac_service
from app.engines.math_engine.penalites_cumul import CCAGCalculator, CCMICalculator
from app.engines.math_engine.margin import MarginAnalyzer
from app.engines.math_engine.treasury import TreasuryAnalyzer
from app.engines.math_engine.capacite_financiere import RatioCalculator, CapaciteFinanciereCalculator
from app.engines.math_engine.chiffrage_pulp import ChiffragePulpSolver, optimiser_chiffrage_chantier
from app.engines.math_engine.bt_projection import BTProjectionCalculator, calculer_projection_bt, generer_bt01
from app.engines.math_engine.mapa_generator import MAPAGenerator, est_mapa, analyser_mapa, generer_devis_mapa
from app.engines.math_engine.pab_detector import PABDetector, detecter_pab, analyser_pab_lots
from app.engines.math_engine.sous_chiffrage import SousChiffrageDetector, detecter_sous_chiffrage
from app.engines.math_engine.worst_case import WorstCaseAnalyzer, analyser_pire_scenario

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/finance", tags=["finance"])


# =============================================================================
# MODÈLES POUR L'API
# =============================================================================

class FinanceInput(BaseModel):
    """Input de base pour les calculs financiers."""
    montant_marche: float
    duree_mois: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "montant_marche": 500000.0,
                "duree_mois": 12
            }
        }


class PenaliteInput(FinanceInput):
    """Input pour les calculs de pénalités."""
    retard_jours: int
    ccag_applicable: bool = True
    ccmi_applicable: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "montant_marche": 500000.0,
                "retard_jours": 20,
                "ccag_applicable": True,
                "ccmi_applicable": False
            }
        }


class MargeInput(FinanceInput):
    """Input pour les calculs de marge."""
    cout_reel: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "montant_marche": 500000.0,
                "cout_reel": 400000.0
            }
        }


class TresorerieInput(FinanceInput):
    """Input pour les calculs de trésorerie."""
    avance_pourcentage: float = 30.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "montant_marche": 500000.0,
                "duree_mois": 12,
                "avance_pourcentage": 30.0
            }
        }


class CapaciteFinanciereInput(BaseModel):
    """Input pour les calculs de capacité financière."""
    capitaux_propres: float
    total_bilan: float
    chiffres_affaires: float
    dettes_financieres: Optional[float] = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "capitaux_propres": 1000000.0,
                "total_bilan": 5000000.0,
                "chiffres_affaires": 2000000.0,
                "dettes_financieres": 500000.0
            }
        }


# =============================================================================
# ENDPOINTS DE PÉNALITÉS
# =============================================================================

@router.post("/penalites/ccag", summary="Calculer pénalité CCAG")
async def calculer_penalite_ccag(
    input: PenaliteInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculer la pénalité selon CCAG Article 14-1.
    
    CCAG: Cahier des Clauses Administratives Générales
    - Retard > 30 jours: 10% du montant
    - Retard 15-30 jours: 5% du montant  
    - Retard < 15 jours: 0.67% par jour
    """
    calculator = CCAGCalculator()
    penalite = calculator.calculer_ccag(
        montant_marche=input.montant_marche,
        retard_jours=input.retard_jours
    )
    
    return {
        "montant_marche": input.montant_marche,
        "retard_jours": input.retard_jours,
        "penalite_montant": round(penalite, 2),
        "penalite_taux": round(penalite / input.montant_marche * 100, 4) if input.montant_marche > 0 else 0,
        "reference": "CCAG Article 14-1"
    }


@router.post("/penalites/ccmi", summary="Calculer pénalité CCMI")
async def calculer_penalite_ccmi(
    input: PenaliteInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculer la pénalité selon CCMI (Cahier des Clauses pour les Marchés de l'Industrie).
    
    CCMI: 1000 € forfaitaire + 1000 € par jour de retard au-delà de 10 jours
    """
    calculator = CCMICalculator()
    penalite = calculator.calculer_ccmi(
        retard_jours=input.retard_jours
    )
    
    return {
        "retard_jours": input.retard_jours,
        "penalite_base": 1000,
        "penalite_jour": max(0, (input.retard_jours - 10)) * 1000,
        "penalite_totale": round(penalite, 2),
        "reference": "CCMI inf+1000"
    }


# =============================================================================
# ENDPOINTS DE MARGE
# =============================================================================

@router.post("/marge/brute", summary="Calculer marge brute")
async def calculer_marge_brute(
    input: MargeInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculer la marge brute: (Montant marché - Coût réel) / Montant marché
    """
    if input.montant_marche <= 0:
        raise HTTPException(status_code=400, detail="Montant marché doit être > 0")
    
    marge_brute = (input.montant_marche - input.cout_reel) / input.montant_marche * 100
    
    return {
        "montant_marche": input.montant_marche,
        "cout_reel": input.cout_reel,
        "marge_brute_pourcentage": round(marge_brute, 4),
        "marge_brute_euro": round(input.montant_marche - input.cout_reel, 2)
    }


@router.post("/marge/analyser", summary="Analyse complète des marges")
async def analyser_marge(
    input: MargeInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyse complète des marges avec calculs détaillés.
    """
    analyzer = MarginAnalyzer()
    
    result = analyzer.analyser_marge(
        montant_marche=input.montant_marche,
        cout_reel=input.cout_reel
    )
    
    return {
        "marge_brute": round(result.marge_brute, 2),
        "marge_brute_pourcentage": round(result.marge_brute_pourcentage, 4),
        "marge_nette": round(result.marge_nette, 2),
        "marge_nette_pourcentage": round(result.marge_nette_pourcentage, 4),
        "marge_commerciale": round(result.marge_commerciale, 2),
        "marge_commerciale_pourcentage": round(result.marge_commerciale_pourcentage, 4),
        "seuil_rentabilite": round(result.seuil_rentabilite, 2),
        "risque_perte": result.risque_perte,
        "recommandations": result.recommandations
    }


# =============================================================================
# ENDPOINTS DE TRÉSORERIE
# =============================================================================

@router.post("/tresorerie/avance", summary="Calculer avance")
async def calculer_avance(
    input: TresorerieInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculer le montant de l'avance (30% par défaut selon P0 2024).
    """
    avance = input.montant_marche * (input.avance_pourcentage / 100)
    
    return {
        "montant_marche": input.montant_marche,
        "avance_pourcentage": input.avance_pourcentage,
        "avance_montant": round(avance, 2)
    }


@router.post("/tresorerie/bfr", summary="Analyse BFR")
async def analyser_bfr(
    input: TresorerieInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyser le Besoin en Fonds de Roulement (BFR) pour un chantier.
    """
    calculator = TreasuryAnalyzer()
    
    # Calcul simplifié du BFR: 10% du montant mensuel moyen
    montant_mensuel = input.montant_marche / (input.duree_mois or 12)
    bfr_moyen = montant_mensuel * 0.10
    
    # Calcul de l'avance
    avance = input.montant_marche * (input.avance_pourcentage / 100)
    
    return {
        "montant_marche": input.montant_marche,
        "duree_mois": input.duree_mois,
        "montant_mensuel": round(montant_mensuel, 2),
        "bfr_moyen": round(bfr_moyen, 2),
        "bfr_total": round(bfr_moyen * (input.duree_mois or 12), 2),
        "avance": round(avance, 2),
        "besoin_tresorerie": round(bfr_moyen * (input.duree_mois or 12) - avance, 2)
    }


@router.post("/bt01/projection", summary="Projection BT01")
async def projection_bt01(
    input: TresorerieInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Générer une projection de trésorerie selon BT01.
    """
    result = calculer_projection_bt(
        montant_marche=input.montant_marche,
        duree_mois=input.duree_mois or 12,
        avance_pourcentage=input.avance_pourcentage
    )
    
    return result


@router.post("/bt01/rapport", summary="Rapport BT01 complet")
async def rapport_bt01(
    input: TresorerieInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Générer un rapport BT01 complet avec recommandations.
    """
    calculator = BTProjectionCalculator()
    rapport = calculator.generer_rapport_bt01(
        montant_marche=input.montant_marche,
        duree_mois=input.duree_mois or 12
    )
    
    return rapport


# =============================================================================
# ENDPOINTS DE CAPACITÉ FINANCIÈRE
# =============================================================================

@router.post("/capacite/ratios", summary="Calculer ratios financiers")
async def calculer_ratios(
    input: CapaciteFinanciereInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Calculer les ratios financiers pour l'analyse de capacité.
    """
    calculator = RatioCalculator()
    
    result = calculator.calculer_tous_ratios(
        capitaux_propres=input.capitaux_propres,
        total_bilan=input.total_bilan,
        chiffres_affaires=input.chiffres_affaires,
        dettes_financieres=input.dettes_financieres or 0
    )
    
    return {
        "autonomie_financiere": round(result.autonomie_financiere, 4),
        "endettement": round(result.endettement, 4),
        "rentabilite_economique": round(result.rentabilite_economique, 4),
        "capacite_remboursement": round(result.capacite_remboursement, 4),
        "fonds_roulement": round(result.fonds_roulement, 2),
        "besoin_fonds_roulement": round(result.besoin_fonds_roulement, 2),
        "trésorerie_nette": round(result.tresorerie_nette, 2)
    }


@router.post("/capacite/verifier", summary="Vérifier capacité financière")
async def verifier_capacite_financiere(
    input: CapaciteFinanciereInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Vérifier la capacité financière selon les seuils légaux.
    """
    calculator = CapaciteFinanciereCalculator()
    
    result = calculator.verifier_capacite(
        capitaux_propres=input.capitaux_propres,
        total_bilan=input.total_bilan,
        chiffres_affaires=input.chiffres_affaires,
        dettes_financieres=input.dettes_financieres or 0
    )
    
    return {
        "est_solvable": result.est_solvable,
        "niveau_risque": result.niveau_risque,
        "capacite_maximale": round(result.capacite_maximale, 2),
        "ratios": {
            "autonomie_financiere": round(result.ratios.autonomie_financiere, 4),
            "endettement": round(result.ratios.endettement, 4),
            "rentabilite": round(result.ratios.rentabilite_economique, 4)
        },
        "recommandations": result.recommandations
    }


# =============================================================================
# ENDPOINTS DE DÉTECTION
# =============================================================================

@router.post("/pab/detecter", summary="Détecter PAB")
async def detecter_pab_endpoint(
    prix_propose: float,
    prix_moyen: float,
    prix_minimal: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Détecter si un prix est anormalement bas (CCAG Article 53).
    """
    result = detecter_pab(prix_propose, prix_moyen, prix_minimal)
    return result


@router.post("/pab/analyser-lots", summary="Analyser lots pour PAB")
async def analyser_pab_lots_endpoint(
    lots: List[Dict[str, float]],
    current_user: dict = Depends(get_current_user)
):
    """
    Analyser plusieurs lots pour la détection PAB.
    """
    result = analyser_pab_lots(lots)
    return result


@router.post("/sous-chiffrage/detecter", summary="Détecter sous-chiffrage")
async def detecter_sous_chiffrage_endpoint(
    estimation: float,
    cout_reel: float,
    taux_marge: float = 0.15,
    current_user: dict = Depends(get_current_user)
):
    """
    Détecter un risque de sous-chiffrage.
    """
    result = detecter_sous_chiffrage(estimation, cout_reel, taux_marge)
    return result


@router.post("/mapa/analyser", summary="Analyser MAPA")
async def analyser_mapa_endpoint(
    montant_ht: float,
    type_acheteur: str = "ETAT",
    current_user: dict = Depends(get_current_user)
):
    """
    Analyser si un marché est éligible à la MAPA.
    """
    result = analyser_mapa(montant_ht, type_acheteur)
    return result


@router.post("/worst-case/analyser", summary="Analyser pire scénario")
async def analyser_worst_case_endpoint(
    risques: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """
    Analyser le pire scénario à partir d'une liste de risques.
    """
    result = analyser_pire_scenario(risques)
    return result

