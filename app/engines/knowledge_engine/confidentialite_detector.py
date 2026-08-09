"""Confidentialité Detector - Détection d'informations sensibles dans les documents"""
import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ConfidentialiteDetector:
    """Détecte les informations confidentielles ou sensibles"""
    
    PATTERNS = {
        "prix_unitaire": r'\b\d+[,\.\d]+\s*€\b',
        "marge": r'(?:marge|coefficient|taux).{0,20}?\d+[,\.\d]+%',
        "strategie": r'(?:notre stratégie|notre approche|méthodologie propriétaire)',
        "sous_traitant": r'(?:sous-traitant|co-traitant).{0,50}?(?:nom|société)',
        "delai_interne": r'(?:délai réel|durée interne).{0,30}?\d+',
        "fournisseur": r'(?:notre fournisseur|partenaire).{0,30}?(?:exclusif|préférentiel)'
    }
    
    def detect(self, text: str) -> Dict:
        """Détecte le niveau de confidentialité d'un texte.

        Retourne un dict conforme aux tests V7.1 :
        {
            "confidential": bool,
            "risk_level": "HIGH" | "MEDIUM" | "NONE",
            "recommended_handler": "local_llm" | "standard",
            "detections": List[Dict]
        }
        """
        detections = []

        for category, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    "category": category,
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8,
                    "action": "mask" if category in ["prix_unitaire", "marge"] else "flag"
                })

        # Mots-clés déclencheurs de confidentialité haute (défense, Seveso, etc.)
        high_confidence_keywords = [
            r"confidentiel\s+d[eé]fense",
            r"secret\s+d[eé]fense",
            r"seveso",
            r"sensible",
            r"classifi[eé]",
        ]
        high_risk = any(
            re.search(kw, text, re.IGNORECASE) for kw in high_confidence_keywords
        )

        if high_risk:
            return {
                "confidential": True,
                "risk_level": "HIGH",
                "recommended_handler": "local_llm",
                "detections": sorted(detections, key=lambda x: x["start"]),
                "markers": sorted(detections, key=lambda x: x["start"]),
            }

        if detections:
            return {
                "confidential": True,
                "risk_level": "MEDIUM",
                "recommended_handler": "standard",
                "detections": sorted(detections, key=lambda x: x["start"]),
                "markers": sorted(detections, key=lambda x: x["start"]),
            }

        return {
            "confidential": False,
            "risk_level": "NONE",
            "recommended_handler": "standard",
            "detections": [],
            "markers": [],
        }
    
    def mask_sensitive_info(self, text: str, detections: List[Dict]) -> str:
        """Masque les informations sensibles détectées"""
        result = text
        offset = 0
        
        for detection in sorted(detections, key=lambda x: x["start"]):
            start = detection["start"] + offset
            end = detection["end"] + offset
            
            if detection["action"] == "mask":
                masked = "[CONFIDENTIEL]"
                result = result[:start] + masked + result[end:]
                offset += len(masked) - (end - start)
        
        return result
    
    def is_document_confidential(self, detections: List[Dict], threshold: int = 3) -> bool:
        """Détermine si un document est globalement confidentiel"""
        high_confidence = [d for d in detections if d["confidence"] > 0.7]
        return len(high_confidence) >= threshold

# Instance globale
detector = ConfidentialiteDetector()


def detect_confidentialite(text: str) -> List[Dict]:
    """Fonction utilitaire qui détecte les informations sensibles dans un texte."""
    return detector.detect(text)
