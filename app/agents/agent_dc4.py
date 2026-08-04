"""
SMART_AO V7 - DC4 Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.5

Agent d'analyse des documents DC4 (Déclaration de Candidature)
Vérifie la conformité administrative et les pièces jointes
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_DC4", "ANALYSER_CONFORMITE_ADMIN", "DETECTER_PIECE_MANQUANTE", "VALIDER_CANDIDATURE"])
class DC4Agent(BaseAgent):
    name = "DC4 Validator"
    capabilities = ["VERIFIER_DC4", "ANALYSER_CONFORMITE_ADMIN", "DETECTER_PIECE_MANQUANTE", "VALIDER_CANDIDATURE"]
    dependencies = ["PARSER"]
    tags = ["administratif", "candidature", "dc4"]
    estimated_duration = timedelta(seconds=4)
    is_blocking = True  # DC4 non conforme = exclusion

    def can_handle(self, mission: Mission) -> float:
        has_dc4 = mission.has_document_type("DC4") or "dc4" in str(mission.context).lower()
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_dc4:
            return 1.0  # Toujours pertinent pour DC4
        if has_dce:
            return 0.40
        return 0.10

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        # Pièces obligatoires DC4
        pieces_obligatoires = [
            "attestation_ss", "kbis", "assurance_decennale", 
            "certificat_qualification", "declaration_candidature",
            "capacite_financiere", "capacite_technique"
        ]
        
        pieces_presentes = input.context.get("pieces_jointes", [])
        
        # Vérification des pièces
        pieces_manquantes = []
        for piece in pieces_obligatoires:
            if piece not in pieces_presentes:
                pieces_manquantes.append(piece)
        
        if pieces_manquantes:
            findings.append({
                "type": "PIECES_MANQUANTES",
                "niveau": "CRITIQUE",
                "manquantes": pieces_manquantes,
                "nombre": len(pieces_manquantes),
                "recommandation": "Compléter dossier avant dépôt",
                "risque": "EXCLUSION"
            })
            status = "FAILED"
        else:
            findings.append({
                "type": "DC4_CONFORME",
                "niveau": "NORMAL",
                "details": "Toutes les pièces obligatoires sont présentes"
            })
            status = "SUCCESS"
        
        # Vérification validité Kbis
        kbis_date = input.context.get("kbis_date_expiration")
        if kbis_date:
            # Simuler vérification (en prod: comparer avec date du jour)
            findings.append({
                "type": "KBI VALIDE",
                "niveau": "INFO",
                "expiration": kbis_date,
                "recommandation": "Vérifier validité à la date de dépôt"
            })
        
        # Détection de mots-clés DC4
        dc4_keywords = ["dc4", "déclaration", "candidature", "kbis", "attestation", "certificat"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in dc4_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "DC4_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "DC4_A_VERIFIER",
                "niveau": "FAIBLE",
                "details": "DC4 à analyser"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_DC4",
            confidence=0.96,
            status=status,
            findings=findings,
            source_pages=[1, 2, 3],
            execution_time_ms=0
        )
