"""
SMART_AO V7 - classifier_47.py
==============================
Classificateur des 47 pièces types des marchés publics BTP.
Identifie et catégorise chaque document du DCE.
"""
import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class Classifier47:
    """Classificateur intelligent des pièces de marchés publics."""

    # Nomenclature officielle des 47 pièces
    PIECES_NOMENCLATURE = {
        "1": "Acte d'engagement (ACT)",
        "2": "Décomposition du prix global et forfaitaire (DPGF)",
        "3": "Bordereau des prix unitaires (BPU)",
        "4": "Détail quantitatif et estimatif (DQE)",
        "5": "Cahier des clauses administratives particulières (CCAP)",
        "6": "Cahier des clauses techniques particulières (CCTP)",
        "7": "Cahier des prescriptions communes (CPC)",
        "8": "Plan général de l'ouvrage",
        "9": "Études géotechniques",
        "10": "Études d'impact environnemental",
        "11": "Règlement de la consultation",
        "12": "Avis d'appel public à la concurrence (AAPC)",
        "13": "Attestations fiscales et sociales",
        "14": "Déclaration sur l'honneur",
        "15": "Pouvoirs de l'acheteur",
        "16": "Procès-verbal de remise des plis",
        "17": "Lettre de candidature",
        "18": "Références similaires",
        "19": "Moyens humains et matériels",
        "20": "Planning prévisionnel",
        "21": "Note méthodologique",
        "22": "Variante technique",
        "23": "Allotissement",
        "24": "Sous-traitance (DC4)",
        "25": "Groupement (DC3)",
        "26": "Chiffre d'affaires (DC2)",
        "27": "Qualifications professionnelles",
        "28": "Assurances décennales",
        "29": "Certificats Qualibat",
        "30": "Normes NF applicables",
        "31": "DTU référencés",
        "32": "Cahier de prescription technique",
        "33": "Nomenclature des prix",
        "34": "Attachements types",
        "35": "Fiches de sécurité",
        "36": "Plan de prévention",
        "37": "Coordination SPS",
        "38": "Étude de prix détaillée",
        "39": "Mémoire technique",
        "40": "Échantillons et maquettes",
        "41": "Protocole d'essai",
        "42": "Rapports de contrôle technique",
        "43": "Autorisations administratives",
        "44": "Servitudes et contraintes",
        "45": "Récolement des réseaux",
        "46": "Dossier de diagnostic technique (DDT)",
        "47": "Amiante et polluants"
    }

    # Mots-clés pour identification automatique
    KEYWORDS_MAPPING = {
        "CCAP": ["cahier des clauses administratives", "ccap", "clauses administratives"],
        "CCTP": ["cahier des clauses techniques", "cctp", "clauses techniques", "prescriptions techniques"],
        "BPU": ["bordereau des prix unitaires", "bpu", "prix unitaire"],
        "DPGF": ["décomposition du prix global", "dpgf", "prix global et forfaitaire"],
        "DQE": ["détail quantitatif", "dqe", "quantitatif estimatif"],
        "ACT": ["acte d'engagement", "act", "engagement"],
        "REGLEMENT": ["règlement de la consultation", "règlement", "modalités"],
        "CCAG": ["cahier des clauses administratives générales", "ccag", "clauses générales"],
        "PLAN": ["plan", "dessin", "schéma"],
        "PAB": ["pab", "particularités administratives", "clause particulière"],
        "PENALITES": ["pénalités", "astreinte", "sanction financière"],
        "DEADLINE": ["délai", "date limite", "échéance", "deadline"],
        "VARIANTES": ["variante", "solution alternative"],
        "SOUS_TRAITANCE": ["sous-traitance", "dc4", "sous-traitant"],
        "GROUPMENT": ["groupement", "cotraitance", "dc3"],
        "AMIANT": ["amiant", "diagnostic", "ddt"],
        "ENVIRONNEMENT": ["environnement", "impact écologique", "hqe"],
        "SECURITE": ["sécurité", "sps", "prévention", "ppspss"]
    }

    def __init__(self):
        self.classification_stats = {
            "documents_classified": 0,
            "unclassified": 0,
            "confidence_scores": []
        }

    async def classify_document(self, text_content: str, filename: str = "") -> Dict[str, Any]:
        """
        Classe un document selon la nomenclature des 47 pièces.
        
        Args:
            text_content: Contenu textuel du document
            filename: Nom du fichier (optionnel)
            
        Returns:
            Dict avec le type identifié et les métadonnées
        """
        logger.debug(f"Classification du document : {filename[:50] if filename else 'inconnu'}")
        
        # Combinaison du contenu et du nom de fichier pour analyse
        analysis_text = f"{filename} {text_content[:2000]}".lower()
        
        best_match = None
        best_score = 0
        matched_keywords = []

        # Recherche par mots-clés
        for piece_type, keywords in self.KEYWORDS_MAPPING.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                occurrences = len(re.findall(r'\b' + re.escape(keyword) + r'\b', analysis_text))
                if occurrences > 0:
                    score += occurrences * 2
                    found_keywords.append(keyword)
            
            # Bonus si trouvé dans le titre/filename
            if filename and any(kw in filename.lower() for kw in keywords):
                score += 10
            
            if score > best_score:
                best_score = score
                best_match = piece_type
                matched_keywords = found_keywords

        # Détermination de la confiance
        confidence = min(best_score / 20.0, 1.0)  # Normalisation 0-1
        
        if confidence < 0.3:
            self.classification_stats["unclassified"] += 1
            return {
                "type": "NON_IDENTIFIE",
                "subtype": None,
                "confidence": confidence,
                "matched_keywords": [],
                "suggested_category": self._suggest_category(text_content),
                "classification_method": "fallback"
            }
        
        self.classification_stats["documents_classified"] += 1
        self.classification_stats["confidence_scores"].append(confidence)
        
        return {
            "type": best_match,
            "subtype": self._get_subtype(best_match, text_content),
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "official_name": self.PIECES_NOMENCLATURE.get(best_match, "Inconnu"),
            "classification_method": "keyword_matching"
        }

    def _get_subtype(self, piece_type: str, text_content: str) -> Optional[str]:
        """Détermine le sous-type si applicable."""
        if piece_type == "CCAP":
            if "marché privé" in text_content.lower():
                return "PRIVE"
            elif "marché public" in text_content.lower():
                return "PUBLIC"
        elif piece_type == "CCTP":
            if "lot unique" in text_content.lower():
                return "LOT_UNIQUE"
            elif "allotissement" in text_content.lower():
                return "ALLOTI"
        return None

    def _suggest_category(self, text_content: str) -> str:
        """Suggère une catégorie générique pour documents non identifiés."""
        text_lower = text_content.lower()
        
        if any(word in text_lower for word in ["prix", "coût", "montant", "euro"]):
            return "FINANCIER"
        elif any(word in text_lower for word in ["technique", "matériau", "mise en oeuvre"]):
            return "TECHNIQUE"
        elif any(word in text_lower for word in ["juridique", "clause", "article", "loi"]):
            return "JURIDIQUE"
        elif any(word in text_lower for word in ["plan", "dessin", "figure"]):
            return "GRAPHIQUE"
        else:
            return "ADMINISTRATIF"

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de classification."""
        scores = self.classification_stats["confidence_scores"]
        avg_confidence = sum(scores) / len(scores) if scores else 0
        
        return {
            **self.classification_stats,
            "average_confidence": round(avg_confidence, 3),
            "success_rate": round(
                self.classification_stats["documents_classified"] / 
                max(self.classification_stats["documents_classified"] + 
                    self.classification_stats["unclassified"], 1) * 100, 2
            )
        }
