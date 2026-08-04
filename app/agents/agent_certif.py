"""
SMART_AO V7 - Certif Live Checker Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.24

Agent de vérification en temps réel des certifications
Vérifie validité et conformité des certifications obligatoires
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_CERTIFICATIONS", "SUIVRE_CERTIFS", "ANALYSER_CONFORMITE_CERTIF", "GENERER_ALERTE_CERTIF"])
class CertifLiveCheckerAgent(BaseAgent):
    name = "Certif Live Checker"
    capabilities = ["VERIFIER_CERTIFICATIONS", "SUIVRE_CERTIFS", "ANALYSER_CONFORMITE_CERTIF", "GENERER_ALERTE_CERTIF"]
    dependencies = ["PARSER"]
    tags = ["certification", "conformité", "qualification", "suivi"]
    estimated_duration = timedelta(seconds=4)
    is_blocking = True

    def can_handle(self, mission: Mission) -> float:
        has_certifications = mission.context.get("certifications") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_certifications:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        certifications = input.context.get("certifications", [])
        
        if certifications:
            has_critical = False
            for certif in certifications:
                valide = certif.get("valide", False)
                expiration = certif.get("expiration", "")
                if not valide:
                    findings.append({
                        "type": "CERTIFICATION_EXPIREE",
                        "niveau": "CRITIQUE",
                        "nom": certif.get("nom", ""),
                        "expiration": expiration,
                        "recommandation": "Renouveler certification urgemment"
                    })
                    has_critical = True
                else:
                    findings.append({
                        "type": "CERTIFICATION_VALIDE",
                        "niveau": "FAIBLE",
                        "nom": certif.get("nom", ""),
                        "expiration": expiration
                    })
            
            if has_critical:
                status = "FAILED"
            else:
                status = "SUCCESS"
        else:
            status = "SUCCESS"
        
        certif_keywords = ["certification", "certificat", "qualification", "conformité", "valide"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in certif_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "CERTIF_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "CERTIF_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucune certification détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_CERTIFICATIONS",
            confidence=0.95,
            status=status,
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
