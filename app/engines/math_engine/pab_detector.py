"""
SMART_AO V7 - pab_detector.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - PAB Detector (Math Engine)
==========================================
Détection mathématique des Prix Anormalement Bas (PAB)
Calcul des seuils et validation selon CCAG

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import statistics

logger = logging.getLogger(__name__)


# Seuil PAB selon CCAG
SEUIL_PAB_30_POURCENT = 0.70  # -30% par rapport au prix moyen
SEUIL_PAB_50_POURCENT = 0.50  # -50% par rapport au prix moyen (vérification renforcée)


@dataclass
class PABResult:
    """Résultat de la détection PAB."""
    est_pab: bool
    niveau_risque: str  # FAIBLE, MOYEN, ELEVE, CRITIQUE
    ecart_pourcentage: float  # % par rapport au prix moyen
    prix_propose: float
    prix_moyen: float
    prix_minimal: Optional[float] = None
    recommandations: List[str] = None
    
    def __post_init__(self):
        if self.recommandations is None:
            self.recommandations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "est_pab": self.est_pab,
            "niveau_risque": self.niveau_risque,
            "ecart_pourcentage": round(self.ecart_pourcentage, 2),
            "prix_propose": round(self.prix_propose, 2),
            "prix_moyen": round(self.prix_moyen, 2),
            "prix_minimal": round(self.prix_minimal, 2) if self.prix_minimal else None,
            "recommandations": self.recommandations
        }


class PABDetector:
    """
    Détecteur mathématique de Prix Anormalement Bas (PAB).
    
    Selon CCAG Article 53:
    - Un prix est anormalement bas s'il est significativement inférieur au prix moyen
    - L'entreprise doit justifier son prix si écart > 30%
    - Refus possible si écart > 50% sans justification valable
    
    Méthode de calcul:
    1. Comparaison avec le prix moyen du marché
    2. Calcul de l'écart en pourcentage
    3. Détermination du niveau de risque
    4. Génération de recommandations
    """
    
    def __init__(self):
        self.result: Optional[PABResult] = None
    
    def detecter_pab(
        self,
        prix_propose: float,
        prix_moyen: float,
        prix_minimal: Optional[float] = None,
        seuil_30: float = SEUIL_PAB_30_POURCENT,
        seuil_50: float = SEUIL_PAB_50_POURCENT
    ) -> PABResult:
        """
        Détecter si un prix est anormalement bas.
        
        Args:
            prix_propose: Prix proposé par l'entreprise (€)
            prix_moyen: Prix moyen du marché (€)
            prix_minimal: Prix minimal acceptable (€) (optionnel)
            seuil_30: Seuil à 30% (0.70)
            seuil_50: Seuil à 50% (0.50)
        
        Returns:
            PABResult: Résultat de la détection
        """
        if prix_moyen <= 0:
            raise ValueError("Le prix moyen doit être supérieur à 0")
        
        # Calculer l'écart
        ecart = prix_propose - prix_moyen
        ecart_pourcentage = (ecart / prix_moyen) * 100
        
        # Déterminer si PAB
        est_pab = prix_propose < prix_moyen * seuil_30
        
        # Déterminer le niveau de risque
        if prix_propose >= prix_moyen:
            niveau_risque = "FAIBLE"
        elif prix_propose >= prix_moyen * seuil_30:
            niveau_risque = "MOYEN"
        elif prix_propose >= prix_moyen * seuil_50:
            niveau_risque = "ELEVE"
        else:
            niveau_risque = "CRITIQUE"
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(
            prix_propose, prix_moyen, ecart_pourcentage, niveau_risque, prix_minimal
        )
        
        self.result = PABResult(
            est_pab=est_pab,
            niveau_risque=niveau_risque,
            ecart_pourcentage=ecart_pourcentage,
            prix_propose=prix_propose,
            prix_moyen=prix_moyen,
            prix_minimal=prix_minimal,
            recommandations=recommandations
        )
        
        return self.result
    
    def _generer_recommandations(
        self,
        prix_propose: float,
        prix_moyen: float,
        ecart_pourcentage: float,
        niveau_risque: str,
        prix_minimal: Optional[float]
    ) -> List[str]:
        """Générer des recommandations basées sur la détection PAB."""
        recommandations = []
        
        if niveau_risque == "FAIBLE":
            recommandations.append("✅ Prix conforme au marché")
            recommandations.append("Aucun risque PAB détecté")
        
        elif niveau_risque == "MOYEN":
            recommandations.append(
                f"⚠️ Prix légèrement inférieur au marché ({ecart_pourcentage:.1f}% d'écart)"
            )
            recommandations.append(
                "Analyser la rentabilité et la stratégie commerciale"
            )
        
        elif niveau_risque == "ELEVE":
            recommandations.append(
                f"🔴 PAB DETECTE: écarts > 30% ({ecart_pourcentage:.1f}%)"
            )
            recommandations.append(
                "CCAG Article 53: Justification obligatoire dans les 48h"
            )
            recommandations.append(
                "Éléments à justifier: coûts réduits, productivité accrue, "
                "innovation, conditions avantageuses"
            )
            
            if prix_minimal and prix_propose < prix_minimal:
                recommandations.append(
                    f"⚠️ Attention: prix inférieur au minimum acceptable ({prix_minimal:.2f} €)"
                )
        
        elif niveau_risque == "CRITIQUE":
            recommandations.append(
                f"💥 PAB CRITIQUE: écarts > 50% ({ecart_pourcentage:.1f}%)"
            )
            recommandations.append(
                "Risque de rejet de l'offre sans justification exceptionnelle"
            )
            recommandations.append(
                "CCAG Article 53-2: L'acheteur peut rejeter l'offre si le prix "
                "est anormalement bas et non justifié"
            )
        
        # Recommandations générales
        if niveau_risque in ["ELEVE", "CRITIQUE"]:
            recommandations.append(
                "📋 Documents à fournir: décomposition des coûts, justificatifs, "
                "attestations de sous-traitants"
            )
            recommandations.append(
                "⏰ Délai: 48h pour fournir les justifications (CCAG)"
            )
        
        return recommandations
    
    def analyser_lot(
        self,
        lots: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Analyser plusieurs lots pour la détection PAB.
        
        Args:
            lots: Liste de lots avec prix_propose et prix_moyen
        
        Returns:
            Dict: Analyse complète par lot
        """
        resultats = {}
        total_pab = 0
        total_lots = len(lots)
        
        for lot in lots:
            prix_propose = lot.get("prix_propose", 0)
            prix_moyen = lot.get("prix_moyen", 0)
            
            if prix_moyen > 0:
                result = self.detecter_pab(prix_propose, prix_moyen)
                resultats[lot.get("nom", "Inconnu")] = result.to_dict()
                
                if result.est_pab:
                    total_pab += 1
        
        return {
            "analyse_par_lot": resultats,
            "total_lots": total_lots,
            "lots_pab": total_pab,
            "pourcentage_pab": round((total_pab / total_lots * 100) if total_lots > 0 else 0, 2),
            "global_est_pab": total_pab > 0
        }
    
    def calculer_seuil_justification(
        self,
        prix_moyen: float,
        seuil: float = SEUIL_PAB_30_POURCENT
    ) -> float:
        """
        Calculer le seuil de prix qui déclenche l'obligation de justification.
        
        Args:
            prix_moyen: Prix moyen du marché (€)
            seuil: Seuil de détection (0.70 pour 30%)
        
        Returns:
            float: Prix seuil (€)
        """
        return prix_moyen * seuil


@dataclass
class PABJustification:
    """Justification d'un prix anormalement bas."""
    elements: List[str]
    economie_realisee: float = 0.0
    risques_identifies: List[str] = None
    documents_fournis: List[str] = None
    
    def __post_init__(self):
        if self.risques_identifies is None:
            self.risques_identifies = []
        if self.documents_fournis is None:
            self.documents_fournis = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "elements": self.elements,
            "economie_realisee": round(self.economie_realisee, 2),
            "risques_identifies": self.risques_identifies,
            "documents_fournis": self.documents_fournis
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def detecter_pab(
    prix_propose: float,
    prix_moyen: float,
    prix_minimal: Optional[float] = None
) -> Dict[str, Any]:
    """
    Détecter si un prix est anormalement bas.
    
    Args:
        prix_propose: Prix proposé (€)
        prix_moyen: Prix moyen du marché (€)
        prix_minimal: Prix minimal acceptable (€)
    
    Returns:
        Résultat de la détection PAB
    """
    detector = PABDetector()
    result = detector.detecter_pab(prix_propose, prix_moyen, prix_minimal)
    return result.to_dict()


def analyser_pab_lots(
    lots: List[Dict[str, float]]
) -> Dict[str, Any]:
    """
    Analyser plusieurs lots pour PAB.
    
    Args:
        lots: Liste de lots avec prix_propose et prix_moyen
    
    Returns:
        Analyse complète
    """
    detector = PABDetector()
    return detector.analyser_lot(lots)


def calculer_seuil_pab(prix_moyen: float) -> float:
    """
    Calculer le seuil PAB à 30%.
    
    Args:
        prix_moyen: Prix moyen du marché (€)
    
    Returns:
        float: Seuil PAB (€)
    """
    detector = PABDetector()
    return detector.calculer_seuil_justification(prix_moyen)


if __name__ == "__main__":
    # Exemple d'utilisation
    detector = PABDetector()
    
    # Test 1: Prix conforme
    print("Test 1 - Prix conforme (100k€ vs 100k€ moyen):")
    result = detector.detecter_pab(100000, 100000)
    print(f"PAB: {result.est_pab}, Niveau: {result.niveau_risque}")
    print(f"Écart: {result.ecart_pourcentage:.1f}%")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Prix à -20%
    print("Test 2 - Prix légèrement inférieur (80k€ vs 100k€ moyen):")
    result = detector.detecter_pab(80000, 100000)
    print(f"PAB: {result.est_pab}, Niveau: {result.niveau_risque}")
    print(f"Écart: {result.ecart_pourcentage:.1f}%")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: PAB à -40%
    print("Test 3 - PAB détecté (60k€ vs 100k€ moyen):")
    result = detector.detecter_pab(60000, 100000)
    print(f"PAB: {result.est_pab}, Niveau: {result.niveau_risque}")
    print(f"Écart: {result.ecart_pourcentage:.1f}%")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 4: PAB critique à -60%
    print("Test 4 - PAB critique (40k€ vs 100k€ moyen):")
    result = detector.detecter_pab(40000, 100000)
    print(f"PAB: {result.est_pab}, Niveau: {result.niveau_risque}")
    print(f"Écart: {result.ecart_pourcentage:.1f}%")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 5: Analyse multi-lots
    print("Test 5 - Analyse multi-lots:")
    lots = [
        {"nom": "Lot 1 - Gros œuvre", "prix_propose": 150000, "prix_moyen": 160000},
        {"nom": "Lot 2 - Électricité", "prix_propose": 45000, "prix_moyen": 50000},
        {"nom": "Lot 3 - Plomberie", "prix_propose": 25000, "prix_moyen": 35000},
        {"nom": "Lot 4 - Peinture", "prix_propose": 8000, "prix_moyen": 10000}
    ]
    analysis = detector.analyser_lot(lots)
    print(f"Lots PAB: {analysis['lots_pab']}/{analysis['total_lots']} ({analysis['pourcentage_pab']}%)")
    for nom, result in analysis['analyse_par_lot'].items():
        print(f"  {nom}: PAB={result['est_pab']}, Niveau={result['niveau_risque']}")

