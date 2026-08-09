"""
SMART_AO V7 - extraction_step.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - extraction_step.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime
import re
import logging

from app.engines.agent_runtime.base_agent import BaseAgent
from app.engines.agent_runtime.registry import agent_registry

logger = logging.getLogger(__name__)


class ExtractionStep(BaseAgent):
    """
    Étape 2 du Workflow : Extraction des données critiques du DCE
    
    Rôle : Extraire automatiquement :
    - Dates limites (deadline submission, deadline questions)
    - Pénalités de retard
    - Plages Acceptables Budgétaires (PAB)
    - Critères de jugement des offres
    - Exigences certifications
    - Clauses administratives particulières (CCAP)
    
    Entrée : Documents parsés (sortie parser_step)
    Sortie : Dict avec données structurées extraites
    """
    
    def __init__(self):
        super().__init__()
        self.agent_id = "extraction_step"
        self.version = "1.0.0"
        self.capabilities = [
            "deadline_extraction",
            "penalty_extraction", 
            "pab_detection",
            "criteria_extraction",
            "certification_requirements",
            "ccap_analysis"
        ]
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute l'extraction des données critiques
        
        Args:
            context: Dictionnaire contenant:
                - parsed_docs: Documents parsés par parser_step
                - raw_text: Texte brut extrait des PDF
                
        Returns:
            Dict avec données extraites structurées
        """
        logger.info("🔍 Démarrage extraction_step - Analyse des données critiques")
        
        try:
            extracted_data = {
                "deadlines": self._extract_deadlines(context),
                "penalties": self._extract_penalties(context),
                "pab": self._detect_pab(context),
                "criteria": self._extract_criteria(context),
                "certifications": self._extract_certifications(context),
                "ccap_clauses": self._extract_ccap_clauses(context),
                "metadata": {
                    "extraction_timestamp": datetime.now().isoformat(),
                    "agent_version": self.version,
                    "confidence_score": 0.0  # Sera calculé
                }
            }
            
            # Calcul du score de confiance global
            extracted_data["metadata"]["confidence_score"] = self._calculate_confidence(extracted_data)
            
            logger.info(f"✅ Extraction terminée - Confiance: {extracted_data['metadata']['confidence_score']:.2f}")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction_step: {e}", exc_info=True)
            raise
    
    def _extract_deadlines(self, context: Dict[str, Any]) -> Dict[str, Optional[datetime]]:
        """Extrait les dates limites du marché"""
        deadlines = {
            "submission_deadline": None,
            "questions_deadline": None,
            "visit_deadline": None,
            "notification_deadline": None
        }
        
        raw_text = context.get("raw_text", "")
        parsed_docs = context.get("parsed_docs", {})
        
        # Patterns de recherche de dates
        date_patterns = [
            r"date\s*limite\s*(?:de\s*)?(?:remise|dépôt|submission)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            r"délai\s*(?:maximal|impératif)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            r"avant\s+le\s+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            r"jusqu'au\s+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            if matches:
                # Conversion format date
                for match in matches[:4]:  # Max 4 dates
                    try:
                        date_obj = self._parse_date(match)
                        if "remise" in pattern or "submission" in pattern.lower():
                            deadlines["submission_deadline"] = date_obj
                        elif "question" in pattern.lower():
                            deadlines["questions_deadline"] = date_obj
                        elif "visite" in pattern.lower():
                            deadlines["visit_deadline"] = date_obj
                        else:
                            deadlines["notification_deadline"] = date_obj
                    except:
                        continue
        
        logger.info(f"📅 Deadlines extraites: {len([d for d in deadlines.values() if d])} dates trouvées")
        return deadlines
    
    def _extract_penalties(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les pénalités de retard"""
        penalties = []
        raw_text = context.get("raw_text", "")
        
        penalty_patterns = [
            r"pénalité(?:s)?\s*(?:de\s*)?retard[:\s]+([\d,]+)\s*(?:€|EUR|pourcent|%)",
            r"retenue(?:s)?\s*(?:pour\s*)?retard[:\s]+([\d,]+)\s*(?:€|EUR|%)",
            r"indemnité(?:s)?\s*(?:de\s*)?retard[:\s]+([\d,]+)\s*(?:€|EUR)"
        ]
        
        for pattern in penalty_patterns:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', '.'))
                    penalty_type = "percentage" if "%" in pattern or "pourcent" in pattern.lower() else "fixed"
                    
                    penalties.append({
                        "amount": amount,
                        "type": penalty_type,
                        "unit": "%" if penalty_type == "percentage" else "EUR",
                        "trigger": "delay_per_day",
                        "source_pattern": pattern
                    })
                except:
                    continue
        
        logger.info(f"💰 Pénalités extraites: {len(penalties)} clauses trouvées")
        return penalties
    
    def _detect_pab(self, context: Dict[str, Any]) -> Optional[Dict[str, Decimal]]:
        """Détecte la Plage Acceptable Budgétaire (PAB)"""
        raw_text = context.get("raw_text", "")
        
        pab_patterns = [
            r"(?:budget\s*(?:estimatif|maximal)|montant\s*(?:prévisionnel|attendu))[:\s]+([\d\s,]+)\s*(?:€|EUR)",
            r"plage\s*(?:acceptable|budgétaire)[\s:]+(?:de\s*)?([\d\s,]+)\s*(?:à|et|-\s*)([\d\s,]+)\s*(?:€|EUR)",
            r"enveloppe\s*(?:financière|budgétaire)[:\s]+([\d\s,]+)\s*(?:€|EUR)"
        ]
        
        for pattern in pab_patterns:
            matches = re.search(pattern, raw_text, re.IGNORECASE)
            if matches:
                try:
                    groups = matches.groups()
                    if len(groups) >= 2 and groups[1]:  # Plage min-max
                        min_amount = Decimal(groups[0].replace(' ', '').replace(',', '.'))
                        max_amount = Decimal(groups[1].replace(' ', '').replace(',', '.'))
                        return {
                            "min": min_amount,
                            "max": max_amount,
                            "currency": "EUR",
                            "detection_method": "range_pattern"
                        }
                    else:  # Montant unique
                        amount = Decimal(groups[0].replace(' ', '').replace(',', '.'))
                        tolerance = Decimal('0.10')  # 10% tolérance par défaut
                        return {
                            "target": amount,
                            "min": amount * (1 - tolerance),
                            "max": amount * (1 + tolerance),
                            "currency": "EUR",
                            "detection_method": "single_amount"
                        }
                except Exception as e:
                    logger.warning(f"Erreur parsing PAB: {e}")
                    continue
        
        logger.info("💷 PAB: Non détectée dans le DCE")
        return None
    
    def _extract_criteria(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les critères de jugement des offres"""
        criteria = []
        raw_text = context.get("raw_text", "")
        
        # Recherche sections critères
        criteria_section = re.search(
            r"(?:critères\s*(?:de\s*)?jugement|attribution|notation|évaluation)[\s\S]*?(?=(?:section|article|clause|$))",
            raw_text, re.IGNORECASE
        )
        
        if criteria_section:
            section_text = criteria_section.group(0)
            
            # Extraction critères pondérés
            weighted_patterns = [
                r"([a-zA-Z\s]+)[:\s]+(\d+)\s*(?:points|%|pourcent)",
                r"(\d+)\s*(?:points|%)\s*[-:]\s*([a-zA-Z\s]+)"
            ]
            
            for pattern in weighted_patterns:
                matches = re.findall(pattern, section_text)
                for match in matches:
                    try:
                        if match[0].isdigit():
                            weight = int(match[0])
                            name = match[1].strip()
                        else:
                            name = match[0].strip()
                            weight = int(match[1])
                        
                        criteria.append({
                            "name": name,
                            "weight": weight,
                            "type": "weighted",
                            "category": self._categorize_criterion(name)
                        })
                    except:
                        continue
        
        logger.info(f"🏆 Critères extraits: {len(criteria)} critères pondérés")
        return criteria
    
    def _extract_certifications(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrait les exigences de certifications"""
        certifications = []
        raw_text = context.get("raw_text", "")
        
        cert_keywords = {
            "ISO 9001": r"ISO\s*9001",
            "ISO 14001": r"ISO\s*14001",
            "ISO 45001": r"ISO\s*45001|OHSAS\s*18001",
            "Qualibat": r"Qualibat",
            "RGE": r"RGE|Reconnu\s*Garant\s*l['\s]Environnement",
            "OPQIBI": r"OPQIBI",
            "NF": r" certification\s*NF|norme\s*NF"
        }
        
        for cert_name, pattern in cert_keywords.items():
            if re.search(pattern, raw_text, re.IGNORECASE):
                certifications.append({
                    "name": cert_name,
                    "required": True,
                    "level": "mandatory"
                })
        
        logger.info(f"📜 Certifications requises: {len(certifications)}")
        return certifications
    
    def _extract_ccap_clauses(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrait les clauses importantes du CCAP"""
        clauses = []
        raw_text = context.get("raw_text", "")
        
        clause_patterns = {
            "payment_terms": r"(?:délai|conditions)\s*(?:de\s*)?paiement[:\s]+([^\.]+)",
            "guarantees": r"(?:garanties?|cautionnements?)[:\s]+([^\.]+)",
            "insurance": r"(?:assurances?|responsabilité\s*civile)[:\s]+([^\.]+)",
            "subcontracting": r"(?:sous-traitance|co-traitance)[:\s]+([^\.]+)"
        }
        
        for clause_type, pattern in clause_patterns.items():
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            for match in matches:
                clauses.append({
                    "type": clause_type,
                    "content": match.strip(),
                    "risk_level": self._assess_clause_risk(clause_type, match)
                })
        
        logger.info(f"📋 Clauses CCAP extraites: {len(clauses)}")
        return clauses
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une chaîne de date en objet datetime"""
        formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
            "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",
            "%Y/%m/%d", "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Format date non reconnu: {date_str}")
        return None
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calcule un score de confiance global sur l'extraction"""
        scores = []
        
        # Score deadlines
        deadlines = data.get("deadlines", {})
        found_deadlines = sum(1 for v in deadlines.values() if v is not None)
        scores.append(found_deadlines / max(len(deadlines), 1))
        
        # Score PAB
        pab = data.get("pab")
        scores.append(1.0 if pab else 0.3)
        
        # Score critères
        criteria = data.get("criteria", [])
        scores.append(min(len(criteria) / 3.0, 1.0))  # Normalisé sur 3 critères
        
        # Moyenne pondérée
        weights = [0.4, 0.3, 0.3]  # Deadlines plus importantes
        confidence = sum(s * w for s, w in zip(scores, weights))
        
        return round(confidence, 2)
    
    def _categorize_criterion(self, name: str) -> str:
        """Catégorise un critère de jugement"""
        name_lower = name.lower()
        
        if "prix" in name_lower or "coût" in name_lower or "financial" in name_lower:
            return "financial"
        elif "technique" in name_lower or "mémoire" in name_lower or "valeur" in name_lower:
            return "technical"
        elif "délai" in name_lower or "calendar" in name_lower:
            return "schedule"
        elif "environnement" in name_lower or "eco" in name_lower:
            return "environmental"
        else:
            return "other"
    
    def _assess_clause_risk(self, clause_type: str, content: str) -> str:
        """Évalue le niveau de risque d'une clause"""
        risk_keywords = {
            "high": ["pénalité", "sanction", "résiliation", "immédiate", "automatique"],
            "medium": ["délai", "condition", "obligation", "justificatif"],
            "low": ["recommandation", "souhaitable", "si possible"]
        }
        
        content_lower = content.lower()
        
        for risk_level, keywords in risk_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return risk_level
        
        return "medium"


# Enregistrement automatique dans le registry
agent_registry.register(ExtractionStep)

# Import statements will be added based on dependencies
# Follow V7 Design Patterns and ADRs

