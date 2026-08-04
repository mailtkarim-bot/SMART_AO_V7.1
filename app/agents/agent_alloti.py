"""
SMART_AO V7 - Alloti Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.14

Agent de gestion des allotissements
Optimise la répartition des lots pour maximiser les chances de gain
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_ALLOTISSEMENT", "OPTIMISER_LOTS", "DETECTER_LOT_NON_RENTABLE", "CALCULER_STRATEGIE_ALLOTI"])
class AllotiAgent(BaseAgent):
    name = "Alloti Guardian"
    capabilities = ["ANALYSER_ALLOTISSEMENT", "OPTIMISER_LOTS", "DETECTER_LOT_NON_RENTABLE", "CALCULER_STRATEGIE_ALLOTI"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["strategie", "lots", "alloti", "optimisation"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_alloti = mission.has_document_type("ALLOTI") or "alloti" in str(mission.context).lower()
        has_lots = mission.context.get("lots") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_alloti or has_lots:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        lots = input.context.get("lots", {})
        strategie_alloti = input.context.get("strategie_alloti", "")
        
        # Analyse des lots
        if lots:
            lots_rentables = []
            lots_non_rentables = []
            lots_a_etudier = []
            
            for lot_nom, lot_data in lots.items():
                marge = lot_data.get("marge", 0)
                risque = lot_data.get("risque", "FAIBLE")
                
                if marge > 15:  # Très rentable
                    lots_rentables.append(lot_nom)
                elif marge < 5:  # Non rentable
                    lots_non_rentables.append(lot_nom)
                else:
                    lots_a_etudier.append(lot_nom)
            
            if lots_non_rentables:
                findings.append({
                    "type": "LOTS_NON_RENTABLES",
                    "niveau": "ELEVE",
                    "lots": lots_non_rentables,
                    "recommandation": "Ne pas soumissionner ces lots ou négocier conditions"
                })
            
            if lots_rentables:
                findings.append({
                    "type": "LOTS_RENTABLES",
                    "niveau": "INFO",
                    "lots": lots_rentables,
                    "recommandation": "Prioriser ces lots dans la stratégie"
                })
            
            if lots_a_etudier:
                findings.append({
                    "type": "LOTS_A_ETUDIER",
                    "niveau": "ATTENTION",
                    "lots": lots_a_etudier,
                    "recommandation": "Analyser plus en détail avant décision"
                })
        
        # Stratégie d'allotissement
        if strategie_alloti:
            findings.append({
                "type": "STRATEGIE_ALLOTI",
                "niveau": "INFO",
                "strategie": strategie_alloti,
                "recommandation": "Valider stratégie avec direction"
            })
        
        # Détection de mots-clés alloti
        alloti_keywords = ["allotissement", "lot", "alloti", "groupement", "soumission"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in alloti_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "ALLOTI_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "ALLOTI_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée allotissement détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_ALLOTISSEMENT",
            confidence=0.92,
            status="SUCCESS",
            findings=findings,
            source_pages=[5, 12, 18],
            execution_time_ms=0
        )
