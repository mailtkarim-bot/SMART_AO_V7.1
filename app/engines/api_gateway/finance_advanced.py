"""
SMART_AO V7 - finance_advanced.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Finance Advanced API
==================================
Endpoints financiers avancés pour l'API Gateway
Calculs complexes et simulations

Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging
from datetime import date, timedelta

from app.core.security import get_current_user
from app.engines.math_engine.chiffrage_pulp import ChiffragePulpSolver, optimiser_chiffrage_chantier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/finance/advanced", tags=["finance-advanced"])


# =============================================================================
# MODÈLES
# =============================================================================

class RessourceInput(BaseModel):
    """Input pour une ressource."""
    nom: str
    cout_unitaire: float
    disponibilite: float
    capacite: Optional[float] = 1.0


class TacheInput(BaseModel):
    """Input pour une tâche."""
    nom: str
    quantite_requise: float
    ressources_requises: Dict[str, float]
    duree_jours: Optional[int] = 1
    priorite: Optional[int] = 1


class OptimisationInput(BaseModel):
    """Input pour l'optimisation de chiffrage."""
    ressources: List[RessourceInput]
    taches: List[TacheInput]


class ScenarioInput(BaseModel):
    """Input pour l'analyse de scénario."""
    montant_marche: float
    duree_mois: int
    coef_risque: Optional[float] = 0.10


class SimulationInput(BaseModel):
    """Input pour la simulation financière."""
    montant_marche: float
    duree_mois: int
    marge_cible: Optional[float] = 0.15
    bfr_pourcentage: Optional[float] = 0.10


# =============================================================================
# ENDPOINTS D'OPTIMISATION
# =============================================================================

@router.post("/chiffrage/optimiser", summary="Optimiser chiffrage avec PuLP")
async def optimiser_chiffrage(
    input: OptimisationInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Optimiser l'affectation des ressources pour minimiser les coûts.
    Utilise PuLP pour la programmation linéaire.
    """
    try:
        result = optimiser_chiffrage_chantier(
            ressources=[r.model_dump() for r in input.ressources],
            taches=[t.model_dump() for t in input.taches]
        )
        return result
    except Exception as e:
        logger.error(f"Erreur d'optimisation: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Erreur d'optimisation: {str(e)}"
        )


@router.post("/chiffrage/simuler", summary="Simuler chiffrage manuel")
async def simuler_chiffrage(
    ressources: List[RessourceInput],
    taches: List[TacheInput],
    current_user: dict = Depends(get_current_user)
):
    """
    Simuler un chiffrage avec affectation manuelle.
    """
    solver = ChiffragePulpSolver()
    
    for r in ressources:
        solver.ajouter_ressource(
            nom=r.nom,
            cout_unitaire=r.cout_unitaire,
            disponibilite=r.disponibilite,
            capacite=r.capacite or 1.0
        )
    
    for t in taches:
        solver.ajouter_tache(
            nom=t.nom,
            quantite_requise=t.quantite_requise,
            ressources_requises=t.ressources_requises,
            duree_jours=t.duree_jours or 1,
            priorite=t.priorite or 1
        )
    
    solution = solver.resolvere()
    
    return {
        "solution": solution.to_dict(),
        "cout_par_tache": solver.calculer_cout_par_tache(),
        "cout_par_ressource": solver.calculer_cout_par_ressource()
    }


# =============================================================================
# ENDPOINTS DE SIMULATION
# =============================================================================

@router.post("/simulation/chantier", summary="Simuler chantier complet")
async def simuler_chantier(
    input: SimulationInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Simuler un chantier complet avec tous les aspects financiers.
    """
    # Calculer l'avance
    avance = input.montant_marche * 0.30
    
    # Calculer le BFR
    montant_mensuel = input.montant_marche / input.duree_mois
    bfr_moyen = montant_mensuel * (input.bfr_pourcentage or 0.10)
    bfr_total = bfr_moyen * input.duree_mois
    
    # Calculer la marge
    marge_totale = input.montant_marche * (input.marge_cible or 0.15)
    
    # Simulation mensuelle
    flux_mensuels = []
    solde_cumule = -bfr_moyen  # BFR initial
    
    for mois in range(1, input.duree_mois + 1):
        avancement = mois / input.duree_mois
        facturation = avancement * input.montant_marche * 0.95  # 5% de rétention
        couts = avancement * input.montant_marche * 0.80
        
        if mois == 1:
            facturation += avance
        
        solde_cumule += facturation - couts
        
        flux_mensuels.append({
            "mois": mois,
            "facturation": round(facturation, 2),
            "couts": round(couts, 2),
            "solde": round(solde_cumule, 2)
        })
    
    # Calculer les indicateurs
    besoin_max = max(abs(f["solde"]) for f in flux_mensuels) if flux_mensuels else 0
    
    return {
        "montant_marche": input.montant_marche,
        "duree_mois": input.duree_mois,
        "marge_cible": input.marge_cible or 0.15,
        "avance": round(avance, 2),
        "bfr_moyen": round(bfr_moyen, 2),
        "bfr_total": round(bfr_total, 2),
        "marge_totale": round(marge_totale, 2),
        "besoin_max": round(besoin_max, 2),
        "flux_mensuels": flux_mensuels,
        "indicateurs": {
            "rentabilite": round(marge_totale / input.montant_marche * 100, 2),
            "besoin_tresorerie": round(besoin_max, 2),
            "ratio_bfr_avance": round(bfr_total / avance * 100, 2) if avance > 0 else 0
        }
    }


@router.post("/simulation/scenarios", summary="Simuler plusieurs scénarios")
async def simuler_scenarios(
    scenarios: List[ScenarioInput],
    current_user: dict = Depends(get_current_user)
):
    """
    Simuler plusieurs scénarios avec différents paramètres.
    """
    resultats = []
    
    for i, scenario in enumerate(scenarios):
        result = simuler_chantier(scenario)
        result["nom_scenario"] = f"Scénario {i + 1}"
        resultats.append(result)
    
    # Calculer les statistiques
    montants = [r["besoin_max"] for r in resultats]
    
    return {
        "scenarios": resultats,
        "statistiques": {
            "besoin_moyen": round(sum(montants) / len(montants), 2) if montants else 0,
            "besoin_min": round(min(montants), 2) if montants else 0,
            "besoin_max": round(max(montants), 2) if montants else 0,
            "nombre_scenarios": len(resultats)
        }
    }


# =============================================================================
# ENDPOINTS DE PRÉVISION
# =============================================================================

@router.post("/prevision/risques", summary="Analyse de risques financiers")
async def analyser_risques_financiers(
    input: ScenarioInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyser les risques financiers d'un chantier.
    """
    # Risques typiques avec probabilités et impacts
    risques = [
        {"nom": "Retard fournisseur", "probabilite": 0.30, "impact": input.montant_marche * 0.05},
        {"nom": "Hausse matériaux", "probabilite": 0.40, "impact": input.montant_marche * 0.08},
        {"nom": "Grève", "probabilite": 0.20, "impact": input.montant_marche * 0.03},
        {"nom": "Contentieux", "probabilite": 0.15, "impact": input.montant_marche * 0.10},
        {"nom": "Pénalités retard", "probabilite": 0.25, "impact": input.montant_marche * 0.07}
    ]
    
    # Calculer le risque total
    risque_total = sum(r["probabilite"] * r["impact"] for r in risques)
    
    # Calculer la perte maximale possible
    perte_maximale = sum(r["impact"] for r in risques)
    
    # Probabilité d'avoir au moins un risque
    prob_aucun = 1.0
    for r in risques:
        prob_aucun *= (1 - r["probabilite"])
    prob_au_moins_un = 1 - prob_aucun
    
    return {
        "montant_marche": input.montant_marche,
        "duree_mois": input.duree_mois,
        "risques": [
            {
                "nom": r["nom"],
                "probabilite": r["probabilite"],
                "impact": round(r["impact"], 2),
                "risque": round(r["probabilite"] * r["impact"], 2)
            }
            for r in risques
        ],
        "risque_total": round(risque_total, 2),
        "perte_maximale": round(perte_maximale, 2),
        "probabilite_risque": round(prob_au_moins_un, 4),
        "provision_recommandee": round(perte_maximale * (input.coef_risque or 0.10), 2),
        "recommandations": [
            f"Prévoir une provision de {round(perte_maximale * 0.10, 2)} € (10% de la perte max)",
            f"Probabilité d'au moins un risque: {prob_au_moins_un*100:.1f}%",
            f"Risque total moyen: {risque_total:.2f} €"
        ]
    }


@router.post("/prevision/tresorerie", summary="Prévision de trésorerie avancée")
async def prevision_tresorerie(
    input: ScenarioInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Prévision de trésorerie avec différents scénarios.
    """
    scenarios = {
        "optimiste": {
            "avancement": lambda m, d: min(m / d * 1.1, 1.0),  # 10% plus rapide
            "couts": lambda m, d: m / d * 0.75,  # 25% de coûts en moins
            "probabilite": 0.25
        },
        "normal": {
            "avancement": lambda m, d: m / d,
            "couts": lambda m, d: m / d * 0.80,
            "probabilite": 0.50
        },
        "pessimiste": {
            "avancement": lambda m, d: m / d * 0.9,  # 10% plus lent
            "couts": lambda m, d: m / d * 0.90,  # 10% de coûts en plus
            "probabilite": 0.25
        }
    }
    
    resultats = {}
    
    for nom, config in scenarios.items():
        solde = -input.montant_marche * 0.10  # BFR initial
        flux = []
        
        for mois in range(1, input.duree_mois + 1):
            avancement = config["avancement"](mois, input.duree_mois)
            facturation = avancement * input.montant_marche * 0.95
            couts = config["couts"](input.montant_marche, input.duree_mois)
            
            if mois == 1:
                facturation += input.montant_marche * 0.30  # Avance
            
            solde += facturation - couts
            flux.append(round(solde, 2))
        
        resultats[nom] = {
            "probabilite": config["probabilite"],
            "solde_final": flux[-1] if flux else 0,
            "besoin_max": max(abs(min(flux)), abs(max(flux))),
            "flux": flux
        }
    
    # Calculer la valeur attendue
    valeur_attendue = sum(
        r["probabilite"] * r["solde_final"] for r in resultats.values()
    )
    
    return {
        "montant_marche": input.montant_marche,
        "duree_mois": input.duree_mois,
        "scenarios": resultats,
        "valeur_attendue": round(valeur_attendue, 2),
        "recommandation": "Privilégier le scénario normal" if valeur_attendue > 0 else "Risque de trésorerie négative"
    }


if __name__ == "__main__":
    # Test rapide
    print("Test Finance Advanced API")
    
    # Test optimisation
    from app.engines.api_gateway.finance_advanced import router
    print(f"Routes disponibles: {[r.path for r in router.routes]}")

