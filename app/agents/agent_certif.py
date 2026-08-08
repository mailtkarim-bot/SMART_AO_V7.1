"""
SMART_AO V7 - agent_certif.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Certif Live Checker Agent
========================================
Agent de vérification des certifications en temps réel.

Référence : RAPPORT (1).md Section 7.24

Responsabilités:
- Vérifier la validité des certifications
- Détecter les certifications expirées
- Alerter sur les certifications manquantes
"""

from typing import Dict, Any, Optional, List
from datetime import date, timedelta
from dataclasses import dataclass, field

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.workflow_engine.mission import Mission


@dataclass
class Certification:
    """Représente une certification."""
    name: str
    cert_id: str
    issue_date: date
    expiry_date: date
    issuer: str
    status: str = "VALID"  # VALID, EXPIRED, REVOKED
    
    def is_valid(self, check_date: date = None) -> bool:
        """Vérifier si la certification est valide."""
        if check_date is None:
            check_date = date.today()
        return self.expiry_date >= check_date and self.status == "VALID"
    
    def days_to_expiry(self, check_date: date = None) -> int:
        """Jours avant expiration."""
        if check_date is None:
            check_date = date.today()
        return (self.expiry_date - check_date).days


class CertifLiveCheckerAgent(BaseAgent):
    """Agent de vérification des certifications en temps réel."""
    
    name = "CertifLiveCheckerAgent"
    capabilities = ["certification_check", "expiry_detection", "compliance_audit"]
    dependencies = ["knowledge_engine"]
    tags = ["certification", "compliance", "legal"]
    estimated_duration = 150  # ms
    is_blocking = True
    
    # Seuils de certification
    EXPIRY_WARNING_DAYS = 30
    EXPIRY_CRITICAL_DAYS = 15

    def __init__(self):
        super().__init__()
        self._certifications: List[Certification] = []
    
    def can_handle(self, input_data: AgentInput) -> bool:
        """Vérifier si l'agent peut traiter l'entrée."""
        # Cet agent peut traiter les missions avec des documents de certification
        if input_data.mission_id:
            mission: Optional[Mission] = self._get_mission(input_data.mission_id)
            if mission and mission.context:
                doc_types = mission.context.get("document_types", [])
                if "certification" in doc_types or "certificat" in doc_types:
                    return True
        
        # Vérifier si c'est une demande explicite de vérification certif
        if input_data.context:
            if input_data.context.get("check_certifications", False):
                return True
        
        return False
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Exécuter la vérification des certifications."""
        # Charger les certifications depuis les documents
        certifications = self._extract_certifications(input_data)
        
        # Vérifier chaque certification
        results = []
        warnings = []
        errors = []
        
        today = date.today()
        
        for cert in certifications:
            result = self._check_certification(cert, today)
            results.append(result)
            
            if not result["is_valid"]:
                if result["status"] == "EXPIRED":
                    errors.append(f"Certification {cert.name} ({cert.cert_id}) EXPIRÉE depuis {(today - cert.expiry_date).days} jours")
                elif result["days_to_expiry"] <= self.EXPIRY_CRITICAL_DAYS:
                    errors.append(f"Certification {cert.name} ({cert.cert_id}) EXPIRE dans {result['days_to_expiry']} jours")
                elif result["days_to_expiry"] <= self.EXPIRY_WARNING_DAYS:
                    warnings.append(f"Certification {cert.name} ({cert.cert_id}) expire bientôt ({result['days_to_expiry']} jours)")
        
        # Générer le rapport
        report = {
            "total_certifications": len(certifications),
            "valid": sum(1 for r in results if r["is_valid"]),
            "expired": sum(1 for r in results if not r["is_valid"] and r["status"] == "EXPIRED"),
            "expiring_soon": sum(1 for r in results if r["days_to_expiry"] <= self.EXPIRY_WARNING_DAYS),
            "details": results,
            "warnings": warnings,
            "errors": errors,
        }
        
        # Déterminer le statut global
        if errors:
            status = "CRITICAL"
        elif warnings:
            status = "WARNING"
        else:
            status = "SUCCESS"
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input_data.mission_id,
            status=status,
            data=report,
            warnings=warnings,
            errors=errors,
            metadata={
                "certifications_checked": len(certifications),
                "check_date": today.isoformat(),
            }
        )
    
    def _extract_certifications(self, input_data: AgentInput) -> List[Certification]:
        """Extraire les certifications des documents."""
        # Implémentation simplifiée - à intégrer avec Knowledge Engine
        certifications = []
        
        # Exemple: Extraire depuis le contexte ou les documents
        if input_data.parsed_docs:
            for doc in input_data.parsed_docs:
                if "certification" in str(doc).lower():
                    # Création d'une certification d'exemple
                    cert = Certification(
                        name="Certificat BTP",
                        cert_id="CERT-2024-001",
                        issue_date=date(2024, 1, 1),
                        expiry_date=date(2024, 12, 31),
                        issuer="Organisme Certificateur"
                    )
                    certifications.append(cert)
        
        # Ajouter des certifications par défaut pour les tests
        if not certifications:
            certifications = [
                Certification(
                    name="Certificat Qualité",
                    cert_id="QUAL-2024-001",
                    issue_date=date(2024, 1, 1),
                    expiry_date=date(2024, 7, 15),  # Expiré
                    issuer="AFNOR"
                ),
                Certification(
                    name="Certificat Sécurité",
                    cert_id="SEC-2024-002",
                    issue_date=date(2024, 6, 1),
                    expiry_date=date(2024, 12, 31),
                    issuer="INRS"
                ),
                Certification(
                    name="Certificat Environnement",
                    cert_id="ENV-2024-003",
                    issue_date=date(2024, 5, 1),
                    expiry_date=date(2024, 8, 10),  # Expire dans 5 jours
                    issuer="ADEME"
                ),
            ]
        
        return certifications
    
    def _check_certification(self, cert: Certification, check_date: date) -> Dict[str, Any]:
        """Vérifier une certification."""
        is_valid = cert.is_valid(check_date)
        days_to_expiry = cert.days_to_expiry(check_date)
        
        if days_to_expiry < 0:
            status = "EXPIRED"
        elif not is_valid:
            status = "REVOKED"
        else:
            status = "VALID"
        
        return {
            "certification_id": cert.cert_id,
            "name": cert.name,
            "issuer": cert.issuer,
            "issue_date": cert.issue_date.isoformat(),
            "expiry_date": cert.expiry_date.isoformat(),
            "is_valid": is_valid,
            "days_to_expiry": days_to_expiry,
            "status": status,
        }
    
    def _get_mission(self, mission_id: str) -> Optional[Mission]:
        """Récupérer une mission (mock pour l'instant)."""
        # À intégrer avec le registry
        try:
            from app.engines.workflow_engine.mission import Mission
            # Return a mock mission for now
            return Mission(id=mission_id, project_id="test", context={"document_types": ["certification"]})
        except:
            return None


# Alias pour compatibilité
CertifAgent = CertifLiveCheckerAgent


# Enregistrement automatique
if __name__ == "__main__":
    from app.engines.agent_runtime.registry import registry
    registry.register(CertifLiveCheckerAgent())
    print(f"✅ {CertifLiveCheckerAgent.name} enregistré dans le registry")
