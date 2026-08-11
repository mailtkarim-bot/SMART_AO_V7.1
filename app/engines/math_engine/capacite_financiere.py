"""
SMART_AO V7 - capacite_financiere.py
======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Capacité Financière Calculator
===============================================
Calcul déterministe de la capacité financière
Séparation complète IA/Déterministe - ZERO LLM
Source: ARCHITECTURE_V7_ENGINE.md §4.3 + ADR-046
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import date, timedelta


# =============================================================================
# ENUMS
# =============================================================================

class CapaciteStatus(str, Enum):
    """Statut de la capacité financière"""
    SUFFISANTE = "suffisante"
    LIMITE = "limite"
    INSUFFISANTE = "insuffisante"
    CRITIQUE = "critique"


class RatioType(str, Enum):
    """Type de ratio financier"""
    AUTONOMIE_FINANCIERE = "autonomie_financiere"
    ENDETTEMENT = "endettement"
    TRESORERIE = "tresorerie"
    BFR = "bfr"
    CAPACITE_REMBOURSEMENT = "capacite_remboursement"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RatioResult:
    """Résultat du calcul d'un ratio financier"""
    type: RatioType
    valeur: float
    seuil_min: float
    seuil_max: float
    unite: str = ""
    statut: CapaciteStatus = CapaciteStatus.SUFFISANTE
    description: str = ""


@dataclass
class CapaciteFinanciereResult:
    """Résultat de l'analyse de capacité financière"""
    score_global: float  # 0-100
    statut: CapaciteStatus
    ratios: Dict[str, RatioResult]
    risques: List[str]
    recommandations: List[str]
    montant_max_marche: float  # Montant max recommandé


# =============================================================================
# CALCULATEUR DE RATIOS FINANCIERS
# =============================================================================

class RatioCalculator:
    """
    Calculateur des ratios financiers BTP
    
    Ratios clés:
    - Autonomie financière = Capitaux propres / Total bilan
    - Endettement = Dettes / Capitaux propres
    - Trésorerie = Liquidités / Dettes à CT
    - BFR = Besoin en Fonds de Roulement
    - Capacité de remboursement = Résultat net / Dettes
    """
    
    # Seuils par défaut pour le BTP
    SEUILS = {
        RatioType.AUTONOMIE_FINANCIERE: {"min": 0.30, "max": 1.00, "ideal": 0.50},
        RatioType.ENDETTEMENT: {"min": 0.00, "max": 1.50, "ideal": 0.70},
        RatioType.TRESORERIE: {"min": 0.50, "max": 2.00, "ideal": 1.00},
        RatioType.BFR: {"min": -0.10, "max": 0.30, "ideal": 0.10},  # BFR en % du CA
        RatioType.CAPACITE_REMBOURSEMENT: {"min": 0.10, "max": 1.00, "ideal": 0.30}
    }
    
    @staticmethod
    def calculer_autonomie_financiere(
        capitaux_propres: float,
        total_bilan: float
    ) -> RatioResult:
        """
        Calculer le ratio d'autonomie financière
        
        Args:
            capitaux_propres: Capitaux propres (EUR)
            total_bilan: Total du bilan (EUR)
        
        Returns:
            RatioResult: Résultat du calcul
        """
        seuils = RatioCalculator.SEUILS[RatioType.AUTONOMIE_FINANCIERE]
        
        if total_bilan <= 0:
            valeur = 0.0
            statut = CapaciteStatus.INSUFFISANTE
        else:
            valeur = capitaux_propres / total_bilan
            
            if valeur >= seuils["ideal"]:
                statut = CapaciteStatus.SUFFISANTE
            elif valeur >= seuils["min"]:
                statut = CapaciteStatus.LIMITE
            else:
                statut = CapaciteStatus.INSUFFISANTE
        
        return RatioResult(
            type=RatioType.AUTONOMIE_FINANCIERE,
            valeur=valeur,
            seuil_min=seuils["min"],
            seuil_max=seuils["max"],
            unite="%",
            statut=statut,
            description="Autonomie financière: capacité à financer ses actifs avec ses capitaux propres"
        )
    
    @staticmethod
    def calculer_endettement(
        dettes: float,
        capitaux_propres: float
    ) -> RatioResult:
        """
        Calculer le ratio d'endettement
        
        Args:
            dettes: Dettes totales (EUR)
            capitaux_propres: Capitaux propres (EUR)
        
        Returns:
            RatioResult: Résultat du calcul
        """
        if capitaux_propres <= 0:
            valeur = float('inf') if dettes > 0 else 0.0
            statut = CapaciteStatus.CRITIQUE
        else:
            valeur = dettes / capitaux_propres
            seuils = RatioCalculator.SEUILS[RatioType.ENDETTEMENT]
            
            if valeur <= seuils["ideal"]:
                statut = CapaciteStatus.SUFFISANTE
            elif valeur <= seuils["max"]:
                statut = CapaciteStatus.LIMITE
            else:
                statut = CapaciteStatus.CRITIQUE
        
        return RatioResult(
            type=RatioType.ENDETTEMENT,
            valeur=valeur,
            seuil_min=seuils["min"],
            seuil_max=seuils["max"],
            unite="",
            statut=statut,
            description="Endettement: niveau de dettes par rapport aux capitaux propres"
        )
    
    @staticmethod
    def calculer_tresorerie(
        liquidites: float,
        dettes_ct: float
    ) -> RatioResult:
        """
        Calculer le ratio de trésorerie
        
        Args:
            liquidites: Liquidités disponibles (EUR)
            dettes_ct: Dettes à court terme (EUR)
        
        Returns:
            RatioResult: Résultat du calcul
        """
        if dettes_ct <= 0:
            valeur = float('inf') if liquidites > 0 else 0.0
            statut = CapaciteStatus.SUFFISANTE
        else:
            valeur = liquidites / dettes_ct
            seuils = RatioCalculator.SEUILS[RatioType.TRESORERIE]
            
            if valeur >= seuils["ideal"]:
                statut = CapaciteStatus.SUFFISANTE
            elif valeur >= seuils["min"]:
                statut = CapaciteStatus.LIMITE
            else:
                statut = CapaciteStatus.INSUFFISANTE
        
        return RatioResult(
            type=RatioType.TRESORERIE,
            valeur=valeur,
            seuil_min=seuils["min"],
            seuil_max=seuils["max"],
            unite="",
            statut=statut,
            description="Trésorerie: capacité à couvrir les dettes à court terme"
        )
    
    @staticmethod
    def calculer_bfr(
        bfr: float,
        chiffre_affaires: float
    ) -> RatioResult:
        """
        Calculer le ratio BFR/CA
        
        Args:
            bfr: Besoin en Fonds de Roulement (EUR)
            chiffre_affaires: Chiffre d'affaires annuel (EUR)
        
        Returns:
            RatioResult: Résultat du calcul
        """
        if chiffre_affaires <= 0:
            valeur = 0.0
            statut = CapaciteStatus.INSUFFISANTE
        else:
            valeur = bfr / chiffre_affaires
            seuils = RatioCalculator.SEUILS[RatioType.BFR]
            
            if valeur <= seuils["ideal"]:
                statut = CapaciteStatus.SUFFISANTE
            elif valeur <= seuils["max"]:
                statut = CapaciteStatus.LIMITE
            else:
                statut = CapaciteStatus.INSUFFISANTE
        
        return RatioResult(
            type=RatioType.BFR,
            valeur=valeur,
            seuil_min=seuils["min"],
            seuil_max=seuils["max"],
            unite="%",
            statut=statut,
            description="BFR: besoin en fonds de roulement par rapport au CA"
        )
    
    @staticmethod
    def calculer_capacite_remboursement(
        resultat_net: float,
        dettes: float
    ) -> RatioResult:
        """
        Calculer le ratio de capacité de remboursement
        
        Args:
            resultat_net: Résultat net (bénéfice ou perte)
            dettes: Dettes totales (EUR)
        
        Returns:
            RatioResult: Résultat du calcul
        """
        if dettes <= 0:
            valeur = float('inf') if resultat_net > 0 else 0.0
            statut = CapaciteStatus.SUFFISANTE
        else:
            valeur = resultat_net / dettes
            seuils = RatioCalculator.SEUILS[RatioType.CAPACITE_REMBOURSEMENT]
            
            if valeur >= seuils["ideal"]:
                statut = CapaciteStatus.SUFFISANTE
            elif valeur >= seuils["min"]:
                statut = CapaciteStatus.LIMITE
            else:
                statut = CapaciteStatus.INSUFFISANTE
        
        return RatioResult(
            type=RatioType.CAPACITE_REMBOURSEMENT,
            valeur=valeur,
            seuil_min=seuils["min"],
            seuil_max=seuils["max"],
            unite="%",
            statut=statut,
            description="Capacité de remboursement: résultat net par rapport aux dettes"
        )


# =============================================================================
# CALCULATEUR DE CAPACITÉ FINANCIÈRE
# =============================================================================

class CapaciteFinanciereCalculator:
    """
    Calculateur de capacité financière globale
    
    Évalue la capacité d'une entreprise à:
    - Financer un nouveau marché
    - Faire face à des imprévus
    - Maintenir sa trésorerie
    """
    
    def __init__(self):
        self.ratio_calculator = RatioCalculator()
    
    def analyser(
        self,
        capitaux_propres: float,
        dettes: float,
        dettes_ct: float,
        liquidites: float,
        bfr: float,
        resultat_net: float,
        chiffre_affaires: float,
        marge_nette: float,
        engagement_max: Optional[float] = None  # Engagement max souhaité (% des capitaux propres)
    ) -> CapaciteFinanciereResult:
        """
        Analyser la capacité financière complète
        
        Args:
            capitaux_propres: Capitaux propres (EUR)
            dettes: Dettes totales (EUR)
            dettes_ct: Dettes à court terme (EUR)
            liquidites: Liquidités disponibles (EUR)
            bfr: Besoin en Fonds de Roulement (EUR)
            resultat_net: Résultat net annuel (EUR)
            chiffre_affaires: Chiffre d'affaires annuel (EUR)
            marge_nette: Marge nette moyenne (%)
            engagement_max: Engagement max souhaité (optionnel, par défaut 30%)
        
        Returns:
            CapaciteFinanciereResult: Analyse complète
        """
        # Calculer tous les ratios
        ratios = {
            "autonomie_financiere": self.ratio_calculator.calculer_autonomie_financiere(
                capitaux_propres, capitaux_propres + dettes
            ),
            "endettement": self.ratio_calculator.calculer_endettement(dettes, capitaux_propres),
            "tresorerie": self.ratio_calculator.calculer_tresorerie(liquidites, dettes_ct),
            "bfr": self.ratio_calculator.calculer_bfr(bfr, chiffre_affaires),
            "capacite_remboursement": self.ratio_calculator.calculer_capacite_remboursement(
                resultat_net, dettes
            )
        }
        
        # Calculer le score global (0-100)
        score_global = self._calculer_score_global(ratios)
        
        # Déterminer le statut global
        statut = self._determiner_statut_global(score_global)
        
        # Identifier les risques
        risques = self._identifier_risques(ratios)
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(ratios, risques)
        
        # Calculer le montant max recommandé pour un marché
        montant_max = self._calculer_montant_max(
            capitaux_propres, dettes, marge_nette, engagement_max
        )
        
        return CapaciteFinanciereResult(
            score_global=score_global,
            statut=statut,
            ratios=ratios,
            risques=risques,
            recommandations=recommandations,
            montant_max_marche=montant_max
        )
    
    def _calculer_score_global(self, ratios: Dict[str, RatioResult]) -> float:
        """
        Calculer le score global (0-100) basé sur les ratios
        
        Args:
            ratios: Dictionnaire des ratios calculés
        
        Returns:
            float: Score global (0-100)
        """
        score = 0.0
        total_weight = 0.0
        
        # Poids par ratio
        poids = {
            "autonomie_financiere": 0.30,
            "endettement": 0.25,
            "tresorerie": 0.25,
            "bfr": 0.10,
            "capacite_remboursement": 0.10
        }
        
        for ratio_name, ratio in ratios.items():
            weight = poids.get(ratio_name, 0.0)
            if weight > 0:
                # Score basé sur la position entre min et max
                if ratio.seuil_max > ratio.seuil_min:
                    # Ratio où plus c'est mieux
                    if ratio.valeur >= ratio.seuil_max:
                        ratio_score = 100.0
                    elif ratio.valeur <= ratio.seuil_min:
                        ratio_score = 0.0
                    else:
                        ratio_score = ((ratio.valeur - ratio.seuil_min) / 
                                      (ratio.seuil_max - ratio.seuil_min)) * 100
                else:
                    # Ratio où moins c'est mieux
                    if ratio.valeur <= ratio.seuil_min:
                        ratio_score = 100.0
                    elif ratio.valeur >= ratio.seuil_max:
                        ratio_score = 0.0
                    else:
                        ratio_score = ((ratio.seuil_max - ratio.valeur) / 
                                      (ratio.seuil_max - ratio.seuil_min)) * 100
                
                score += ratio_score * weight
                total_weight += weight
        
        if total_weight > 0:
            score = score / total_weight
        
        return round(score, 2)
    
    def _determiner_statut_global(self, score: float) -> CapaciteStatus:
        """
        Déterminer le statut global basé sur le score
        
        Args:
            score: Score global (0-100)
        
        Returns:
            CapaciteStatus: Statut global
        """
        if score >= 80:
            return CapaciteStatus.SUFFISANTE
        elif score >= 60:
            return CapaciteStatus.LIMITE
        elif score >= 30:
            return CapaciteStatus.INSUFFISANTE
        else:
            return CapaciteStatus.CRITIQUE
    
    def _identifier_risques(self, ratios: Dict[str, RatioResult]) -> List[str]:
        """
        Identifier les risques basé sur les ratios
        
        Args:
            ratios: Dictionnaire des ratios calculés
        
        Returns:
            List[str]: Liste des risques identifiés
        """
        risques = []
        
        for ratio_name, ratio in ratios.items():
            if ratio.statut == CapaciteStatus.CRITIQUE:
                risques.append(f"Ratio {ratio_name} CRITIQUE: {ratio.description}")
            elif ratio.statut == CapaciteStatus.INSUFFISANTE:
                risques.append(f"Ratio {ratio_name} insuffisant: {ratio.description}")
        
        return risques
    
    def _generer_recommandations(
        self, 
        ratios: Dict[str, RatioResult], 
        risques: List[str]
    ) -> List[str]:
        """
        Générer des recommandations basé sur les ratios
        
        Args:
            ratios: Dictionnaire des ratios calculés
            risques: Liste des risques identifiés
        
        Returns:
            List[str]: Liste des recommandations
        """
        recommandations = []
        
        # Recommandations basées sur les ratios
        if ratios["autonomie_financiere"].statut != CapaciteStatus.SUFFISANTE:
            recommandations.append(
                "Augmenter les capitaux propres (apport en capital, bénéfices non distribués)"
            )
        
        if ratios["endettement"].statut != CapaciteStatus.SUFFISANTE:
            recommandations.append(
                "Réduire l'endettement (remboursement de dettes, augmentation des capitaux propres)"
            )
        
        if ratios["tresorerie"].statut != CapaciteStatus.SUFFISANTE:
            recommandations.append(
                "Améliorer la trésorerie (négocier délais fournisseurs, accélérer encaissements)"
            )
        
        if ratios["bfr"].statut != CapaciteStatus.SUFFISANTE:
            recommandations.append(
                "Optimiser le BFR (réduire stocks, négocier délais de paiement)"
            )
        
        if ratios["capacite_remboursement"].statut != CapaciteStatus.SUFFISANTE:
            recommandations.append(
                "Améliorer la rentabilité pour augmenter la capacité de remboursement"
            )
        
        return recommandations
    
    def _calculer_montant_max(
        self,
        capitaux_propres: float,
        dettes: float,
        marge_nette: float,
        engagement_max: Optional[float] = None
    ) -> float:
        """
        Calculer le montant maximum recommandé pour un marché
        
        Args:
            capitaux_propres: Capitaux propres (EUR)
            dettes: Dettes totales (EUR)
            marge_nette: Marge nette moyenne (%)
            engagement_max: Engagement max souhaité (% des capitaux propres)
        
        Returns:
            float: Montant maximum recommandé (EUR)
        """
        if engagement_max is None:
            engagement_max = 30.0  # 30% par défaut
        
        # Montant max basé sur les capitaux propres
        montant_max_cp = capitaux_propres * (engagement_max / 100)
        
        # Montant max basé sur la capacité de remboursement
        # On considère qu'un marché ne devrait pas dépasser 2 ans de résultat net
        if marge_nette > 0:
            resultat_annuel_estime = capitaux_propres * (marge_nette / 100)
            montant_max_remboursement = resultat_annuel_estime * 2
        else:
            montant_max_remboursement = 0
        
        # Prendre le minimum des deux
        montant_max = min(montant_max_cp, montant_max_remboursement)
        
        return round(montant_max, 2)


# =============================================================================
# UTILITIES
# =============================================================================

def calculer_capacite_financiere(
    capitaux_propres: float,
    dettes: float,
    liquidites: float,
    bfr: float,
    resultat_net: float,
    chiffre_affaires: float
) -> float:
    """
    Calculer rapidement le score de capacité financière
    
    Args:
        capitaux_propres: Capitaux propres (EUR)
        dettes: Dettes totales (EUR)
        liquidites: Liquidités (EUR)
        bfr: BFR (EUR)
        resultat_net: Résultat net (EUR)
        chiffre_affaires: Chiffre d'affaires (EUR)
    
    Returns:
        float: Score de capacité financière (0-100)
    """
    calculator = CapaciteFinanciereCalculator()
    result = calculator.analyser(
        capitaux_propres, dettes, dettes, liquidites, bfr, resultat_net, chiffre_affaires, 10.0
    )
    return result.score_global


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

capacite_financiere_calculator = CapaciteFinanciereCalculator()


def get_capacite_financiere_calculator() -> CapaciteFinanciereCalculator:
    """Get the singleton CapaciteFinanciereCalculator instance"""
    return capacite_financiere_calculator
