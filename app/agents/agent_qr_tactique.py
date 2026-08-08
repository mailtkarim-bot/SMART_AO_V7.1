"""
SMART_AO V7 - agent_qr_tactique.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - QR Tactique Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.10

Agent de questions/réponses tactiques sur les DCE
Fournit des réponses ciblées pour la stratégie de réponse aux appels d'offres
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["QR_TACTIQUE", "REPONDRE_QUESTION_DCE", "ANALYSER_STRATEGIE", "GENERER_REPONSE_OPTIMALE"])
class QRTactiqueAgent(BaseAgent):
    name = "QR Tactique"
    capabilities = ["QR_TACTIQUE", "REPONDRE_QUESTION_DCE", "ANALYSER_STRATEGIE", "GENERER_REPONSE_OPTIMALE"]
    dependencies = ["PARSER", "KNOWLEDGE_ENGINE"]
    tags = ["strategie", "q&r", "tactique", "dce"]
    estimated_duration = timedelta(seconds=10)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_questions = mission.context.get("questions_dce") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_questions:
            return 0.98
        if has_dce:
            return 0.50
        return 0.15

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        questions = input.context.get("questions_dce", [])
        
        # Analyse des questions DCE
        if questions:
            for i, question in enumerate(questions, 1):
                niveau = question.get("niveau", "INFO")
                thematique = question.get("thematique", "")
                
                # Réponse tactique
                if "prix" in thematique.lower() or "coût" in thematique.lower():
                    findings.append({
                        "type": "QUESTION_FINANCIERE",
                        "niveau": niveau,
                        "question": question.get("texte", ""),
                        "thematique": thematique,
                        "reponse_tactique": "Analyser marché et proposer prix compétitif avec marge minimale",
                        "recommandation": "Consulter Math Engine pour optimisation"
                    })
                elif "délai" in thematique.lower() or "planning" in thematique.lower():
                    findings.append({
                        "type": "QUESTION_DELAI",
                        "niveau": niveau,
                        "question": question.get("texte", ""),
                        "thematique": thematique,
                        "reponse_tactique": "Proposer planning réaliste avec marge de sécurité",
                        "recommandation": "Vérifier Deadline Guardian"
                    })
                elif "technique" in thematique.lower():
                    findings.append({
                        "type": "QUESTION_TECHNIQUE",
                        "niveau": niveau,
                        "question": question.get("texte", ""),
                        "thematique": thematique,
                        "reponse_tactique": "Démontrer expertise et conformité aux exigences",
                        "recommandation": "Consulter CCTP et DPGF"
                    })
                else:
                    findings.append({
                        "type": "QUESTION_GENERALE",
                        "niveau": niveau,
                        "question": question.get("texte", ""),
                        "thematique": thematique,
                        "reponse_tactique": "Réponse standard conforme aux bonnes pratiques"
                    })
        
        # Détection de mots-clés QR
        qr_keywords = ["question", "réponse", "tactique", "stratégie", "q&r"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in qr_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "QR_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "AUCUNE_QUESTION",
                "niveau": "FAIBLE",
                "details": "Aucune question DCE détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="QR_TACTIQUE",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[2, 5, 10],
            execution_time_ms=0
        )
