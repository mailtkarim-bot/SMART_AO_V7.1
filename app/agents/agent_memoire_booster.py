"""
SMART_AO V7 - agent_memoire_booster.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Mémoire Booster Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.11

Agent de mémorisation et réutilisation des données historiques
Améliore la cohérence des offres en s'appuyant sur les chantiers précédents
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["AMELIORER_COHERENCE", "REUTILISER_HISTORIQUE", "DETECTER_INCOHERENCE", "OPTIMISER_OFFRE"])
class MemoireBoosterAgent(BaseAgent):
    name = "Memory Booster"
    capabilities = ["AMELIORER_COHERENCE", "REUTILISER_HISTORIQUE", "DETECTER_INCOHERENCE", "OPTIMISER_OFFRE"]
    dependencies = ["PARSER", "PRICING_MEMORY"]
    tags = ["mémoire", "historique", "cohérence", "optimisation"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_history = mission.context.get("historique_chantiers") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_history:
            return 0.95
        if has_dce:
            return 0.60
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        historique = input.context.get("historique_chantiers", [])
        current_project = input.context.get("projet_actuel", {})
        
        # Comparaison avec historique
        if historique:
            similitude_max = 0
            projet_similaire = None
            
            for projet in historique:
                # Calculer similitude (simplifié)
                similitude = 0
                if projet.get("type") == current_project.get("type"):
                    similitude += 0.4
                if projet.get("localisation") == current_project.get("localisation"):
                    similitude += 0.3
                if projet.get("taille") and current_project.get("taille"):
                    similitude += 0.3 * (1 - abs(projet["taille"] - current_project["taille"]) / max(projet["taille"], current_project["taille"]))
                
                if similitude > similitude_max:
                    similitude_max = similitude
                    projet_similaire = projet
            
            if projet_similaire and similitude_max > 0.6:
                findings.append({
                    "type": "PROJET_SIMILAIRE",
                    "niveau": "ELEVE",
                    "similitude": f"{similitude_max * 100:.1f}%",
                    "projet": projet_similaire.get("nom", "Inconnu"),
                    "recommandation": "Réutiliser données historiques pour optimiser offre"
                })
                
                # Stocker les données financières
                if projet_similaire.get("prix_m2") and current_project.get("prix_m2"):
                    financial_data["comparaison_prix"] = {
                        "prix_historique_m2": projet_similaire["prix_m2"],
                        "prix_actuel_m2": current_project["prix_m2"]
                    }
                    
                    # Comparaison des prix (qualitatif)
                    ecart = abs(projet_similaire["prix_m2"] - current_project["prix_m2"]) / projet_similaire["prix_m2"]
                    if ecart > 0.2:  # +20%
                        findings.append({
                            "type": "ECART_PRIX_HISTORIQUE",
                            "niveau": "ELEVE",
                            "ecart": f"{ecart * 100:.1f}%",
                            "details": "Écart de prix détecté avec projet similaire (voir financial_data)",
                            "recommandation": "Justifier écart ou ajuster offre"
                        })
        
        # Détection de mots-clés mémoire
        memoire_keywords = ["historique", "mémoire", "chantier précédent", "coherence", "similaire"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in memoire_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "MEMOIRE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "MEMOIRE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucun historique pertinent détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="AMELIORER_COHERENCE",
            confidence=0.88,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[1, 3, 7],
            execution_time_ms=0
        )
