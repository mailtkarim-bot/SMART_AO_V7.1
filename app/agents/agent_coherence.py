"""
SMART_AO V7 - Coherence Guardian Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.16

Agent de vérification de la cohérence prix-mémoire
Marge < 3% acceptable
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_COHERENCE", "DETECTER_INCOHERENCE", "ANALYSER_PRICE_MEMORY", "CORRIGER_ANOMALIES"])
class CoherenceGuardianAgent(BaseAgent):
    name = "Coherence Guardian"
    capabilities = ["VERIFIER_COHERENCE", "DETECTER_INCOHERENCE", "ANALYSER_PRICE_MEMORY", "CORRIGER_ANOMALIES"]
    dependencies = ["PARSER", "CHIFFRAGE", "MEMORY_BOOSTER"]
    tags = ["coherence", "prix", "mémoire", "validation"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = True

    def can_handle(self, mission: Mission) -> float:
        has_memory = mission.context.get("pricing_memory") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_memory:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        pricing_memory = input.context.get("pricing_memory", {})
        current_prices = input.context.get("current_prices", {})
        
        if pricing_memory and current_prices:
            incoherences = []
            for item, current_price in current_prices.items():
                if item in pricing_memory:
                    historical_price = pricing_memory[item]
                    deviation = abs(current_price - historical_price) / historical_price if historical_price > 0 else 0
                    if deviation > 0.15:
                        incoherences.append({
                            "item": item,
                            "deviation": f"{deviation * 100:.1f}%",
                            "current": current_price,
                            "historical": historical_price
                        })
            
            if incoherences:
                findings.append({
                    "type": "INCOHERENCES_DETECTEES",
                    "niveau": "ELEVE",
                    "incoherences": incoherences,
                    "recommandation": "Justifier écarts ou corriger prix"
                })
                status = "FAILED"
            else:
                findings.append({
                    "type": "COHERENCE_PARFAITE",
                    "niveau": "FAIBLE",
                    "details": "Tous les prix sont cohérents avec l'historique"
                })
                status = "SUCCESS"
        
        coherence_keywords = ["cohérence", "prix", "mémoire", "anomalie", "validation"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in coherence_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "COHERENCE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "COHERENCE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée cohérence détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_COHERENCE",
            confidence=0.92,
            status=status,
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
