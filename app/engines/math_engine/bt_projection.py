"""
SMART_AO V7 - bt_projection.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - BT Projection Solver
===================================
Projection du Besoin en Trésorerie (BT) selon BT01
Calcul des flux de trésorerie mensuels et validation de la conformité BT01

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class FluxTresorerie:
    """Représente un flux de trésorerie mensuel."""
    mois: int  # 1-12
    annee: int
    entrees: float = 0.0  # € (avances, paiements clients)
    sorties: float = 0.0  # € (fournisseurs, salaires, charges)
    solde: float = 0.0  # € (solde cumulé)
    
    @property
    def solde_cumule(self) -> float:
        """Calcul du solde cumulé."""
        return self.entrees - self.sorties


@dataclass
class ProjectionBT:
    """Projection complète du Besoin en Trésorerie."""
    montant_marche: float
    duree_mois: int
    avance_pourcentage: float = 30.0  # P0 2024: 30%
    retentions_pourcentage: float = 5.0  # Rétention de garantie
    taux_marge: float = 0.15  # Marge moyenne BTP
    
    flux_mensuels: List[FluxTresorerie] = None
    besoin_max: float = 0.0
    mois_besoin_max: int = 0
    est_conforme_bt01: bool = True
    
    def __post_init__(self):
        if self.flux_mensuels is None:
            self.flux_mensuels = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "montant_marche": round(self.montant_marche, 2),
            "duree_mois": self.duree_mois,
            "avance_pourcentage": self.avance_pourcentage,
            "retentions_pourcentage": self.retentions_pourcentage,
            "taux_marge": self.taux_marge,
            "besoin_max": round(self.besoin_max, 2),
            "mois_besoin_max": self.mois_besoin_max,
            "est_conforme_bt01": self.est_conforme_bt01,
            "flux_mensuels": [
                {
                    "mois": f.mois,
                    "annee": f.annee,
                    "entrees": round(f.entrees, 2),
                    "sorties": round(f.sorties, 2),
                    "solde": round(f.solde, 2)
                }
                for f in self.flux_mensuels
            ]
        }


class BTProjectionCalculator:
    """
    Calculateur de projection de trésorerie selon BT01.
    
    BT01 (Bordereau de Trésorerie) est un document obligatoire pour les marchés publics
    qui prouve que l'entreprise a la capacité financière à exécuter le chantier.
    
    Calcul:
    - Avance initiale (30% du marché)
    - Facturation mensuelle selon avancement
    - Rétention de garantie (5%)
    - Besoin en fonds de roulement (BFR)
    """
    
    def __init__(self):
        self.projection: Optional[ProjectionBT] = None
    
    def calculer_projection(
        self,
        montant_marche: float,
        duree_mois: int,
        avance_pourcentage: float = 30.0,
        retentions_pourcentage: float = 5.0,
        taux_marge: float = 0.15,
        date_debut: Optional[date] = None
    ) -> ProjectionBT:
        """
        Calculer la projection de trésorerie.
        
        Args:
            montant_marche: Montant HT du marché (€)
            duree_mois: Durée du chantier en mois
            avance_pourcentage: Pourcentage d'avance (défaut 30%)
            retentions_pourcentage: Pourcentage de rétention (défaut 5%)
            taux_marge: Taux de marge (défaut 15%)
            date_debut: Date de début du chantier
        
        Returns:
            ProjectionBT: La projection complète
        """
        if date_debut is None:
            date_debut = date.today()
        
        # Calculer l'avance initiale
        avance = montant_marche * (avance_pourcentage / 100)
        
        # Calculer le montant à facturer (hors rétention)
        montant_a_facturer = montant_marche * (1 - retentions_pourcentage / 100)
        
        # Calculer la marge
        marge_totale = montant_marche * taux_marge
        
        # Calculer le BFR moyen (10% du montant mensuel)
        bfr_moyen = (montant_a_facturer / duree_mois) * 0.10
        
        # Générer les flux mensuels
        flux_mensuels = []
        solde_cumule = -bfr_moyen  # BFR initial à financer
        besoin_max = abs(solde_cumule)
        mois_besoin_max = 1
        
        for mois in range(1, duree_mois + 1):
            # Calculer l'avancement (S-curve simplifiée)
            if duree_mois <= 12:
                # Pour les petits chantiers: linéaire
                avancement = mois / duree_mois
            else:
                # Pour les grands chantiers: S-curve
                t = mois / duree_mois
                avancement = t * t * (3 - 2 * t)  # S-curve: 0→1
            
            # Facturation mensuelle (proportionnelle à l'avancement)
            facturation_mensuelle = (avancement - ((mois - 1) / duree_mois)) * montant_a_facturer
            
            # Coûts mensuels (simplifiés: 80% du montant proportionnel)
            # Inclut: main d'oeuvre, matériaux, sous-traitance
            couts_mensuels = (avancement - ((mois - 1) / duree_mois)) * (montant_marche * 0.80)
            
            # Calculer les flux
            entrees = facturation_mensuelle
            sorties = couts_mensuels + bfr_moyen  # BFR à financer chaque mois
            
            if mois == 1:
                entrees += avance  # Avance reçu au début
            
            solde_cumule += entrees - sorties
            
            flux = FluxTresorerie(
                mois=mois,
                annee=date_debut.year + ((date_debut.month + mois - 1) // 12),
                entrees=entrees,
                sorties=sorties,
                solde=solde_cumule
            )
            flux_mensuels.append(flux)
            
            # Mettre à jour le besoin max
            if abs(solde_cumule) > besoin_max:
                besoin_max = abs(solde_cumule)
                mois_besoin_max = mois
        
        # Vérifier la conformité BT01
        # BT01 exige que l'entreprise ait au moins 10% du montant du marché en trésorerie
        capacite_financiere_requise = montant_marche * 0.10
        est_conforme_bt01 = besoin_max <= capacite_financiere_requise
        
        # Créer la projection
        self.projection = ProjectionBT(
            montant_marche=montant_marche,
            duree_mois=duree_mois,
            avance_pourcentage=avance_pourcentage,
            retentions_pourcentage=retentions_pourcentage,
            taux_marge=taux_marge,
            flux_mensuels=flux_mensuels,
            besoin_max=besoin_max,
            mois_besoin_max=mois_besoin_max,
            est_conforme_bt01=est_conforme_bt01
        )
        
        return self.projection
    
    def calculer_seuil_bt01(self, montant_marche: float) -> float:
        """
        Calculer le seuil minimal de trésorerie pour BT01.
        
        BT01 exige que l'entreprise ait une trésorerie minimale de:
        - 10% du montant du marché pour les marchés < 500k€
        - 5% du montant du marché pour les marchés >= 500k€
        
        Args:
            montant_marche: Montant HT du marché (€)
        
        Returns:
            float: Seuil minimal de trésorerie (€)
        """
        if montant_marche < 500000:
            return montant_marche * 0.10
        else:
            return montant_marche * 0.05
    
    def generer_rapport_bt01(self, montant_marche: float, duree_mois: int) -> Dict[str, Any]:
        """
        Générer un rapport BT01 complet.
        
        Args:
            montant_marche: Montant HT du marché (€)
            duree_mois: Durée du chantier en mois
        
        Returns:
            Dict: Rapport BT01 avec tous les indicateurs
        """
        projection = self.calculer_projection(montant_marche, duree_mois)
        
        rapport = {
            "montant_marche": round(montant_marche, 2),
            "duree_mois": duree_mois,
            "avance": round(montant_marche * 0.30, 2),
            "retention": round(montant_marche * 0.05, 2),
            "marge_estimee": round(montant_marche * 0.15, 2),
            "seuil_bt01": round(self.calculer_seuil_bt01(montant_marche), 2),
            "besoin_max": round(projection.besoin_max, 2),
            "mois_besoin_max": projection.mois_besoin_max,
            "est_conforme": projection.est_conforme_bt01,
            "recommandations": []
        }
        
        # Ajouter des recommandations
        if not projection.est_conforme_bt01:
            rapport["recommandations"].append(
                f"Trésorerie insuffisante: besoin max de {projection.besoin_max:.2f} € "
                f"mais seuil BT01 est {self.calculer_seuil_bt01(montant_marche):.2f} €"
            )
            rapport["recommandations"].append(
                "Solutions: augmenter l'avance, négocier des paiements plus fréquents, "
                "ou obtenir un prêt de trésorerie"
            )
        
        rapport["recommandations"].append(
            f"Prévoir un BFR moyen de {round((montant_marche / duree_mois) * 0.10, 2)} €/mois"
        )
        
        return rapport


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def calculer_projection_bt(
    montant_marche: float,
    duree_mois: int,
    avance_pourcentage: float = 30.0
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour calculer une projection BT.
    
    Args:
        montant_marche: Montant HT du marché (€)
        duree_mois: Durée du chantier en mois
        avance_pourcentage: Pourcentage d'avance
    
    Returns:
        Dictionnaire avec la projection BT
    """
    calculator = BTProjectionCalculator()
    projection = calculator.calculer_projection(
        montant_marche, duree_mois, avance_pourcentage
    )
    return projection.to_dict()


def generer_bt01(
    montant_marche: float,
    duree_mois: int
) -> Dict[str, Any]:
    """
    Générer un rapport BT01 complet.
    
    Args:
        montant_marche: Montant HT du marché (€)
        duree_mois: Durée du chantier en mois
    
    Returns:
        Rapport BT01 complet
    """
    calculator = BTProjectionCalculator()
    return calculator.generer_rapport_bt01(montant_marche, duree_mois)


if __name__ == "__main__":
    # Exemple d'utilisation
    calculator = BTProjectionCalculator()
    
    # Chantier de 500k€ sur 12 mois
    projection = calculator.calculer_projection(500000, 12)
    print("Projection BT:")
    print(f"Montant marché: {projection.montant_marche:.2f} €")
    print(f"Durée: {projection.duree_mois} mois")
    print(f"Besoin max: {projection.besoin_max:.2f} € (mois {projection.mois_besoin_max})")
    print(f"Conforme BT01: {projection.est_conforme_bt01}")
    
    # Rapport BT01
    rapport = calculator.generer_rapport_bt01(500000, 12)
    print("\nRapport BT01:")
    for key, value in rapport.items():
        print(f"{key}: {value}")

