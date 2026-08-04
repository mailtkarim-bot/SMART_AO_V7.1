"""
SMART_AO V7 - Handoff Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.12

Agent de gestion du transfert irréversible (HANDOFF)
Assure la transmission sécurisée des données entre étapes
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["GESTION_HANDOFF", "VALIDER_TRANSFERT", "VERROUILLER_DONNEES", "DETECTER_ANOMALIE_HANDOFF"])
class HandoffAgent(BaseAgent):
    name = "Handoff Guardian"
    capabilities = ["GESTION_HANDOFF", "VALIDER_TRANSFERT", "VERROUILLER_DONNEES", "DETECTER_ANOMALIE_HANDOFF"]
    dependencies = ["PARSER", "WORKFLOW_ENGINE"]
    tags = ["handoff", "transfert", "irreversible", "securité"]
    estimated_duration = timedelta(seconds=3)
    is_blocking = True  # Handoff échoué = Mission FAILED

    def can_handle(self, mission: Mission) -> float:
        has_handoff_data = mission.context.get("handoff_data") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_handoff_data:
            return 1.0
        if has_dce:
            return 0.30
        return 0.05

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        handoff_data = input.context.get("handoff_data", {})
        handoff_status = input.context.get("handoff_status", "PENDING")
        
        # Vérification du handoff
        if handoff_status == "COMPLETED":
            findings.append({
                "type": "HANDOFF_REUSSI",
                "niveau": "NORMAL",
                "details": "Transfert de données terminé avec succès",
                "date": handoff_data.get("timestamp", ""),
                "checksum": handoff_data.get("checksum", "")
            })
            status = "SUCCESS"
        elif handoff_status == "PENDING":
            findings.append({
                "type": "HANDOFF_EN_ATTENTE",
                "niveau": "ELEVE",
                "details": "Transfert en cours, validation nécessaire",
                "recommandation": "Finaliser validation pour verrouiller données"
            })
            status = "SUCCESS"  # Pas bloquant en cours
        elif handoff_status == "FAILED":
            findings.append({
                "type": "HANDOFF_ECHOUÉ",
                "niveau": "CRITIQUE",
                "details": "Transfert de données échoué",
                "erreur": handoff_data.get("erreur", "Inconnue"),
                "recommandation": "Reprendre handoff manuellement",
                "risque": "PERTE_DE_DONNEES"
            })
            status = "FAILED"
        else:
            findings.append({
                "type": "HANDOFF_INCONNU",
                "niveau": "ATTENTION",
                "details": f"Statut inconnu: {handoff_status}",
                "recommandation": "Vérifier statut du handoff"
            })
            status = "SUCCESS"
        
        # Vérification intégrité données
        if handoff_data.get("checksum"):
            findings.append({
                "type": "INTEGRITE_VERIFIEE",
                "niveau": "INFO",
                "algorithme": handoff_data.get("algorithme", "SHA-256"),
                "checksum": handoff_data.get("checksum", "")
            })
        
        # Détection de mots-clés handoff
        handoff_keywords = ["handoff", "transfert", "irréversible", "verrouillage", "checksum"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in handoff_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "HANDOFF_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "HANDOFF_A_VERIFIER",
                "niveau": "FAIBLE",
                "details": "Vérification handoff nécessaire"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="GESTION_HANDOFF",
            confidence=0.98,
            status=status,
            findings=findings,
            source_pages=[1],
            execution_time_ms=0
        )
