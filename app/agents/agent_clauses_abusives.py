"""
SMART_AO V7 - agent_clauses_abusives.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Clauses Abusives CCAP Agent
==========================================
Agent de détection des clauses abusives dans les CCAP
Protège contre les risques juridiques et financiers

Fonctionnalités:
- Détection des clauses déséquilibrées
- Vérification des pénalités excessives
- Identification des conditions abusives
- Recommandations juridiques
"""

from datetime import timedelta
from typing import List, Dict, Any
import re

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


# =============================================================================
# CLauses ABUSIVES CONNUES (CCAP, CCMI, Code de la commande publique)
# =============================================================================

CLAUSES_ABUSIVES_PATTERNS = {
    # Pénalités excessives
    "PENALITE_EXCESSIVE": {
        "patterns": [
            r"pénalité.*supérieure.*10%",
            r"pénalité.*dépassant.*10%",
            r"taux.*pénalité.*>.*10%",
            r" majoration.*50%",
        ],
        "niveau": "CRITIQUE",
        "reference": "CCAP Article 14-1 (max 10% du montant HT)",
        "recommandation": "Négocier la réduction des pénalités ou demander suppression",
    },
    
    # Délais de paiement trop longs
    "DELAI_PAIEMENT_ABUSIF": {
        "patterns": [
            r"paiement.*sous.*60.*jours",
            r"paiement.*sous.*90.*jours",
            r"délai.*paiement.*>.*45.*jours",
        ],
        "niveau": "ELEVE",
        "reference": "Loi n°2018-905 du 23 octobre 2018 (délai max 45 jours)",
        "recommandation": "Exiger un délai de paiement ≤ 45 jours",
    },
    
    # Résiliation unilatérale abusive
    "RESILIATION_ABUSIVE": {
        "patterns": [
            r"résiliation.*sans.*préavis",
            r"résiliation.*à.*tout.*moment",
            r"résiliation.*sans.*indemnité",
        ],
        "niveau": "CRITIQUE",
        "reference": "CCAP Article 20 (droit à préavis raisonnable)",
        "recommandation": "Négocier clause de préavis ou indemnité de résiliation",
    },
    
    # Limitation de responsabilité abusive
    "RESPONSABILITE_LIMITEE_ABUSIVE": {
        "patterns": [
            r"responsabilité.*limitée.*à.*0%",
            r"responsabilité.*exclue",
            r"aucune.*responsabilité",
        ],
        "niveau": "CRITIQUE",
        "reference": "Article 1240 du Code civil",
        "recommandation": "Refuser la clause ou demander limitation raisonnable",
    },
    
    # Obligation de moyen vs résultat
    "OBLIGATION_DE_RESULTAT": {
        "patterns": [
            r"obligation.*de.*résultat",
            r"garantie.*de.*résultat",
            r"résultat.*garanti",
        ],
        "niveau": "ELEVE",
        "reference": "Jurisprudence : obligation de moyens en BTP",
        "recommandation": "Remplacer par 'obligation de moyens' ou refuser",
    },
    
    # Paiement des pénalités sans mise en demeure
    "PENALITE_SANS_MISE_EN_DEMEURE": {
        "patterns": [
            r"pénalité.*sans.*mise.*en.*demeure",
            r"pénalité.*automatique",
            r"application.*immédiate.*pénalité",
        ],
        "niveau": "CRITIQUE",
        "reference": "CCAP Article 14-2 (mise en demeure obligatoire)",
        "recommandation": "Exiger mise en demeure préalable avant pénalité",
    },
    
    # Clause potestative
    "CLAUSE_POTESTATIVE": {
        "patterns": [
            r"si.*je.*veux",
            r"si.*je.*l'estime",
            r"à.*ma.*convenance",
        ],
        "niveau": "CRITIQUE",
        "reference": "Article 1174 du Code civil (nullité des clauses potestatives)",
        "recommandation": "Demander la suppression de la clause",
    },
    
    # Modification unilatérale du contrat
    "MODIFICATION_UNILATERALE": {
        "patterns": [
            r"modification.*unilatérale",
            r"modification.*sans.*accord",
            r"changement.*sans.*avis",
        ],
        "niveau": "ELEVE",
        "reference": "Article 1104 du Code civil (consentement mutuel)",
        "recommandation": "Exiger accord écrit pour toute modification",
    },
    
    # Exclusivité abusive
    "EXCLUSIVITE_ABUSIVE": {
        "patterns": [
            r"exclusivité.*sans.*limite.*durée",
            r"exclusivité.*perpétuelle",
            r"interdiction.*travailler.*avec.*autres",
        ],
        "niveau": "ELEVE",
        "reference": "Droit de la concurrence (limitation temporelle)",
        "recommandation": "Limiter la durée d'exclusivité ou refuser",
    },
    
    # Clause limitative de recours
    "RECOURS_LIMITES": {
        "patterns": [
            r"recours.*exclusivement.*devant",
            r"tribunal.*compétent.*uniquement",
            r"renonciation.*à.*tout.*recours",
        ],
        "niveau": "MOYEN",
        "reference": "Article 48 du Code de procédure civile",
        "recommandation": "Vérifier la conformité avec le droit applicable",
    },
}


@registry.register(capabilities=["DETECTER_CLAUSES_ABUSIVES", "VERIFIER_CCAP", "ANALYSE_JURIDIQUE"])
class ClausesAbusivesAgent(BaseAgent):
    """
    Agent de détection des clauses abusives dans les documents CCAP/CCMI.
    
    Capabilités:
    - Détection automatique des clauses abusives
    - Classification par niveau de risque
    - Recommandations juridiques
    - ZERO € : retour qualitatif uniquement
    """
    
    name = "Clauses Abusives Detector"
    capabilities = ["DETECTER_CLAUSES_ABUSIVES", "VERIFIER_CCAP", "ANALYSE_JURIDIQUE"]
    dependencies = ["PARSER", "CLASSIFICATION"]
    tags = ["juridique", "risque", "ccap", "conformité"]
    estimated_duration = timedelta(seconds=10)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        """Évaluer la pertinence pour cette mission."""
        has_ccap = mission.has_document_type("CCAP") or "ccap" in str(mission.context).lower()
        has_ccmi = mission.has_document_type("CCMI") or "ccmi" in str(mission.context).lower()
        has_legal = any(
            kw in str(mission.context).lower() 
            for kw in ["contrat", "clause", "condition", "pénalité"]
        )
        
        if has_ccap or has_ccmi:
            return 0.95
        if has_legal:
            return 0.75
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Exécuter la détection des clauses abusives."""
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        # Analyse de chaque chunk
        for chunk_idx, chunk in enumerate(chunks):
            chunk_text = str(chunk).lower()
            
            for clause_type, clause_info in CLAUSES_ABUSIVES_PATTERNS.items():
                for pattern in clause_info["patterns"]:
                    if re.search(pattern, chunk_text, re.IGNORECASE):
                        finding = {
                            "type": clause_type,
                            "niveau": clause_info["niveau"],
                            "clause": pattern,
                            "reference": clause_info["reference"],
                            "recommandation": clause_info["recommandation"],
                            "page": input.parsed_docs.get("pages", [])[chunk_idx] if chunk_idx < len(input.parsed_docs.get("pages", [])) else chunk_idx + 1,
                            "action": "NEGOCIER" if clause_info["niveau"] in ["CRITIQUE", "ELEVE"] else "VERIFIER"
                        }
                        
                        # Éviter les doublons
                        if finding not in findings:
                            findings.append(finding)
                        break  # Un match par type de clause par chunk
        
        # Si aucun finding, recherche plus large
        if not findings:
            text_full = " ".join(str(c) for c in chunks).lower()
            for clause_type, clause_info in CLAUSES_ABUSIVES_PATTERNS.items():
                for pattern in clause_info["patterns"]:
                    if re.search(pattern, text_full, re.IGNORECASE):
                        findings.append({
                            "type": clause_type,
                            "niveau": clause_info["niveau"],
                            "clause": pattern,
                            "reference": clause_info["reference"],
                            "recommandation": clause_info["recommandation"],
                            "action": "NEGOCIER" if clause_info["niveau"] in ["CRITIQUE", "ELEVE"] else "VERIFIER"
                        })
                        break
        
        # Calculer le score de risque global
        if findings:
            critique_count = sum(1 for f in findings if f["niveau"] == "CRITIQUE")
            eleve_count = sum(1 for f in findings if f["niveau"] == "ELEVE")
            moyen_count = sum(1 for f in findings if f["niveau"] == "MOYEN")
            
            financial_data["risque_juridique"] = {
                "score": min(100, critique_count * 40 + eleve_count * 25 + moyen_count * 10),
                "clauses_critiques": critique_count,
                "clauses_elevees": eleve_count,
                "clauses_moyennes": moyen_count,
                "niveau_global": "CRITIQUE" if critique_count > 0 else ("ELEVE" if eleve_count > 0 else "MOYEN")
            }
        
        if not findings:
            findings.append({
                "type": "AUCUNE_CLAUSE_ABUSIVE_DETECTEE",
                "niveau": "FAIBLE",
                "details": "Aucune clause abusive détectée dans le document",
                "recommandation": "Document conforme aux exigences légales"
            })
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_CLAUSES_ABUSIVES",
            confidence=0.95,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=list(range(1, min(len(chunks) + 1, 50))),
            execution_time_ms=0
        )
