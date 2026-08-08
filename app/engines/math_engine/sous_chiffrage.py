"""
SMART_AO V7 - sous_chiffrage.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Sous-Chiffrage Detector
=====================================
Détection et calcul des risques de sous-chiffrage
Analyse des écarts entre estimation et coût réel

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# Seuil de détection
SEUIL_RISQUE_FAIBLE = 0.05  # 5% d'écart
SEUIL_RISQUE_MOYEN = 0.10  # 10% d'écart
SEUIL_RISQUE_ELEVE = 0.20  # 20% d'écart


@dataclass
class SousChiffrageResult:
    """Résultat de la détection de sous-chiffrage."""
    est_sous_chiffre: bool
    niveau_risque: str  # FAIBLE, MOYEN, ELEVE, CRITIQUE
    ecart_absolu: float  # €
    ecart_relatif: float  # %
    estimation: float
    cout_reel: float
    marge_perdue: float = 0.0
    recommandations: List[str] = None
    
    def __post_init__(self):
        if self.recommandations is None:
            self.recommandations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "est_sous_chiffre": self.est_sous_chiffre,
            "niveau_risque": self.niveau_risque,
            "ecart_absolu": round(self.ecart_absolu, 2),
            "ecart_relatif": round(self.ecart_relatif * 100, 2),
            "estimation": round(self.estimation, 2),
            "cout_reel": round(self.cout_reel, 2),
            "marge_perdue": round(self.marge_perdue, 2),
            "recommandations": self.recommandations
        }


class SousChiffrageDetector:
    """
    Détecteur de risques de sous-chiffrage.
    
    Fonctionnalités:
    - Détection des écarts entre estimation et réalité
    - Calcul de la marge perdue
    - Analyse des causes possibles
    - Génération de recommandations
    """
    
    def __init__(self, taux_marge_cible: float = 0.15):
        self.taux_marge_cible = taux_marge_cible
        self.result: Optional[SousChiffrageResult] = None
    
    def detecter_sous_chiffrage(
        self,
        estimation: float,
        cout_reel: float,
        taux_marge_cible: Optional[float] = None
    ) -> SousChiffrageResult:
        """
        Détecter un risque de sous-chiffrage.
        
        Args:
            estimation: Montant estimé (€)
            cout_reel: Coût réel engendré (€)
            taux_marge_cible: Taux de marge cible (défaut 15%)
        
        Returns:
            SousChiffrageResult: Résultat de l'analyse
        """
        if taux_marge_cible is None:
            taux_marge_cible = self.taux_marge_cible
        
        # Calculer l'écart
        ecart_absolu = cout_reel - estimation
        
        if estimation > 0:
            ecart_relatif = ecart_absolu / estimation
        else:
            ecart_relatif = 0
        
        # Déterminer si sous-chiffrage
        est_sous_chiffre = cout_reel > estimation
        
        # Déterminer le niveau de risque
        if not est_sous_chiffre:
            niveau_risque = "FAIBLE"
        elif ecart_relatif <= SEUIL_RISQUE_FAIBLE:
            niveau_risque = "MOYEN"
        elif ecart_relatif <= SEUIL_RISQUE_MOYEN:
            niveau_risque = "ELEVE"
        elif ecart_relatif <= SEUIL_RISQUE_ELEVE:
            niveau_risque = "CRITIQUE"
        else:
            niveau_risque = "CATASTROPHIQUE"
        
        # Calculer la marge perdue
        marge_prevue = estimation * taux_marge_cible
        marge_reelle = estimation - cout_reel  # Peut être négative
        marge_perdue = marge_prevue - marge_reelle
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(
            estimation, cout_reel, ecart_absolu, ecart_relatif, niveau_risque
        )
        
        self.result = SousChiffrageResult(
            est_sous_chiffre=est_sous_chiffre,
            niveau_risque=niveau_risque,
            ecart_absolu=ecart_absolu,
            ecart_relatif=ecart_relatif,
            estimation=estimation,
            cout_reel=cout_reel,
            marge_perdue=marge_perdue,
            recommandations=recommandations
        )
        
        return self.result
    
    def _generer_recommandations(
        self,
        estimation: float,
        cout_reel: float,
        ecart_absolu: float,
        ecart_relatif: float,
        niveau_risque: str
    ) -> List[str]:
        """Générer des recommandations basées sur l'analyse."""
        recommandations = []
        
        if niveau_risque == "FAIBLE":
            recommandations.append("✅ Pas de sous-chiffrage détecté")
            recommandations.append("Marge préservée")
        
        elif niveau_risque == "MOYEN":
            recommandations.append(
                f"⚠️ Léger dépassement: +{ecart_absolu:.2f} € ({ecart_relatif*100:.1f}%)"
            )
            recommandations.append(
                "Analyser les causes: hausse des matériaux, main d'oeuvre supplémentaire"
            )
        
        elif niveau_risque == "ELEVE":
            recommandations.append(
                f"🔴 Sous-chiffrage significatif: +{ecart_absolu:.2f} € ({ecart_relatif*100:.1f}%)"
            )
            recommandations.append(
                "Actions immédiates: négocier avec le client, trouver des économies"
            )
            recommandations.append(
                "Documenter les causes pour les futurs chantiers"
            )
        
        elif niveau_risque == "CRITIQUE":
            recommandations.append(
                f"💥 Sous-chiffrage critique: +{ecart_absolu:.2f} € ({ecart_relatif*100:.1f}%)"
            )
            recommandations.append(
                "Urgence: arrêt partiel du chantier si nécessaire"
            )
            recommandations.append(
                "Analyse complète des coûts avec le service études"
            )
        
        elif niveau_risque == "CATASTROPHIQUE":
            recommandations.append(
                f"💀 Sous-chiffrage catastrophique: +{ecart_absolu:.2f} € ({ecart_relatif*100:.1f}%)"
            )
            recommandations.append(
                "Risque de perte totale sur ce chantier"
            )
            recommandations.append(
                "Nécessité de renégocier le contrat ou abandonner le chantier"
            )
        
        # Recommandations générales
        if niveau_risque in ["ELEVE", "CRITIQUE", "CATASTROPHIQUE"]:
            recommandations.append(
                "📊 Mettre à jour les bases de données de chiffrage"
            )
            recommandations.append(
                "⏰ Réviser les processus d'estimation"
            )
        
        return recommandations
    
    def analyser_chantier_complet(
        self,
        lots: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Analyser un chantier complet (multi-lots) pour le sous-chiffrage.
        
        Args:
            lots: Liste de lots avec estimation et cout_reel
        
        Returns:
            Dict: Analyse complète
        """
        resultats = {}
        total_sous_chiffre = 0
        marge_perdue_totale = 0
        
        for lot in lots:
            estimation = lot.get("estimation", 0)
            cout_reel = lot.get("cout_reel", 0)
            
            if estimation > 0:
                result = self.detecter_sous_chiffrage(estimation, cout_reel)
                resultats[lot.get("nom", "Inconnu")] = result.to_dict()
                
                if result.est_sous_chiffre:
                    total_sous_chiffre += 1
                marge_perdue_totale += result.marge_perdue
        
        return {
            "analyse_par_lot": resultats,
            "total_lots": len(lots),
            "lots_sous_chiffres": total_sous_chiffre,
            "marge_perdue_totale": round(marge_perdue_totale, 2),
            "global_est_sous_chiffre": total_sous_chiffre > 0
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def detecter_sous_chiffrage(
    estimation: float,
    cout_reel: float,
    taux_marge: float = 0.15
) -> Dict[str, Any]:
    """
    Détecter un sous-chiffrage.
    
    Args:
        estimation: Montant estimé (€)
        cout_reel: Coût réel (€)
        taux_marge: Taux de marge cible
    
    Returns:
        Résultat de la détection
    """
    detector = SousChiffrageDetector(taux_marge)
    result = detector.detecter_sous_chiffrage(estimation, cout_reel)
    return result.to_dict()


def analyser_sous_chiffrage_chantier(
    lots: List[Dict[str, float]]
) -> Dict[str, Any]:
    """
    Analyser un chantier pour le sous-chiffrage.
    
    Args:
        lots: Liste de lots avec estimation et cout_reel
    
    Returns:
        Analyse complète
    """
    detector = SousChiffrageDetector()
    return detector.analyser_chantier_complet(lots)


if __name__ == "__main__":
    # Exemple d'utilisation
    detector = SousChiffrageDetector()
    
    # Test 1: Pas de sous-chiffrage
    print("Test 1 - Chantier rentable (estimation: 100k€, coût: 85k€):")
    result = detector.detecter_sous_chiffrage(100000, 85000)
    print(f"Sous-chiffrage: {result.est_sous_chiffre}, Niveau: {result.niveau_risque}")
    print(f"Écart: +{result.ecart_absolu:.2f} € ({result.ecart_relatif*100:.1f}%)")
    print(f"Marge perdue: {result.marge_perdue:.2f} €")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Sous-chiffrage léger
    print("Test 2 - Sous-chiffrage léger (estimation: 100k€, coût: 105k€):")
    result = detector.detecter_sous_chiffrage(100000, 105000)
    print(f"Sous-chiffrage: {result.est_sous_chiffre}, Niveau: {result.niveau_risque}")
    print(f"Écart: +{result.ecart_absolu:.2f} € ({result.ecart_relatif*100:.1f}%)")
    print(f"Marge perdue: {result.marge_perdue:.2f} €")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Sous-chiffrage significatif
    print("Test 3 - Sous-chiffrage significatif (estimation: 100k€, coût: 125k€):")
    result = detector.detecter_sous_chiffrage(100000, 125000)
    print(f"Sous-chiffrage: {result.est_sous_chiffre}, Niveau: {result.niveau_risque}")
    print(f"Écart: +{result.ecart_absolu:.2f} € ({result.ecart_relatif*100:.1f}%)")
    print(f"Marge perdue: {result.marge_perdue:.2f} €")
    print(f"Recommandations: {result.recommandations}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 4: Sous-chiffrage critique
    print("Test 4 - Sous-chiffrage critique (estimation: 100k€, coût: 150k€):")
    result = detector.detecter_sous_chiffrage(100000, 150000)
    print(f"Sous-chiffrage: {result.est_sous_chiffre}, Niveau: {result.niveau_risque}")
    print(f"Écart: +{result.ecart_absolu:.2f} € ({result.ecart_relatif*100:.1f}%)")
    print(f"Marge perdue: {result.marge_perdue:.2f} €")
    print(f"Recommandations: {result.recommandations}")

