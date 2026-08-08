"""
SMART_AO V7 - margin.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Margin Calculator
================================
Calcul déterministe des marges et coefficients
Séparation complète IA/Déterministe - ZERO LLM
Source: ARCHITECTURE_V7_ENGINE.md §4.3 + ADR-046
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class MarginType(str, Enum):
    """Type de marge"""
    BRUTE = "brute"
    NETTE = "nette"
    COMMERCIALE = "commerciale"
    CIBLE = "cible"


class CoefficientType(str, Enum):
    """Type de coefficient"""
    VENTE = "coeff_vente"
    PRODUCTION = "coeff_production"
    SOUS_TRAITANCE = "coeff_sous_traitance"
    RISQUE = "coeff_risque"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CoefficientResult:
    """Résultat du calcul d'un coefficient"""
    type: CoefficientType
    valeur: float
    description: str
    reference: str = ""
    details: Optional[Dict[str, Any]] = None


@dataclass
class MarginResult:
    """Résultat du calcul de marge"""
    type: MarginType
    montant: float
    pourcentage: float
    base_calcul: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class MarginAnalysis:
    """Analyse complète des marges"""
    marge_brute: MarginResult
    marge_nette: MarginResult
    marge_commerciale: MarginResult
    coefficients: Dict[str, CoefficientResult]
    marge_cible: Optional[MarginResult] = None
    ecart_vs_cible: float = 0.0
    niveau_risque: str = "FAIBLE"


# =============================================================================
# CALCULATEUR DE COEFFICIENTS
# =============================================================================

class CoefficientCalculator:
    """
    Calculateur des coefficients appliqués au marché
    
    Coefficients typiques BTP:
    - Coefficient de vente: 1.1 à 1.3 (marge commerciale)
    - Coefficient de production: 0.8 à 1.0 (coûts de production)
    - Coefficient de sous-traitance: 1.05 à 1.25 (surcharge sous-traitants)
    - Coefficient de risque: 1.02 à 1.15 (marge de sécurité)
    """
    
    # Coefficients par défaut (à personnaliser par entreprise)
    DEFAULT_COEFFICIENTS = {
        CoefficientType.VENTE: {
            "valeur": 1.20,
            "description": "Coefficient de vente standard (20% de marge)",
            "min": 1.05,
            "max": 1.50
        },
        CoefficientType.PRODUCTION: {
            "valeur": 0.90,
            "description": "Coefficient de production (10% de coûts indirects)",
            "min": 0.70,
            "max": 1.00
        },
        CoefficientType.SOUS_TRAITANCE: {
            "valeur": 1.10,
            "description": "Coefficient de sous-traitance (10% de surcharge)",
            "min": 1.00,
            "max": 1.30
        },
        CoefficientType.RISQUE: {
            "valeur": 1.05,
            "description": "Coefficient de risque (5% de marge de sécurité)",
            "min": 1.00,
            "max": 1.20
        }
    }
    
    def calculer(
        self,
        coefficient_type: CoefficientType,
        custom_value: Optional[float] = None
    ) -> CoefficientResult:
        """
        Calculer un coefficient
        
        Args:
            coefficient_type: Type de coefficient
            custom_value: Valeur personnalisée (optionnelle)
        
        Returns:
            CoefficientResult: Résultat du calcul
        """
        default = self.DEFAULT_COEFFICIENTS.get(coefficient_type, {})
        
        if custom_value is not None:
            valeur = custom_value
            description = f"Coefficient {coefficient_type.value} personnalisé"
        else:
            valeur = default.get("valeur", 1.0)
            description = default.get("description", "Coefficient par défaut")
        
        return CoefficientResult(
            type=coefficient_type,
            valeur=valeur,
            description=description,
            reference=f"COEFF_{coefficient_type.value}",
            details={
                "min": default.get("min"),
                "max": default.get("max"),
                "custom": custom_value is not None
            }
        )
    
    def calculer_tous(self) -> Dict[str, CoefficientResult]:
        """
        Calculer tous les coefficients par défaut
        
        Returns:
            Dict[str, CoefficientResult]: Tous les coefficients
        """
        coefficients = {}
        for coeff_type in CoefficientType:
            result = self.calculer(coeff_type)
            coefficients[coeff_type.value] = result
        
        return coefficients


# =============================================================================
# CALCULATEUR DE MARGES
# =============================================================================

class MarginCalculator:
    """
    Calculateur des marges
    
    Formules:
    - Marge brute = Chiffre d'affaires - Coût de revient
    - Marge nette = Marge brute - Charges
    - Marge commerciale = (CA * coefficient_vente) - CA
    - Marge cible = Objectif défini par l'entreprise
    """
    
    @staticmethod
    def calculer_marge_brute(
        chiffre_affaires: float,
        cout_revient: float
    ) -> MarginResult:
        """
        Calculer la marge brute
        
        Args:
            chiffre_affaires: Chiffre d'affaires HT
            cout_revient: Coût de revient total
        
        Returns:
            MarginResult: Marge brute calculée
        """
        marge = chiffre_affaires - cout_revient
        pourcentage = (marge / chiffre_affaires * 100) if chiffre_affaires > 0 else 0
        
        return MarginResult(
            type=MarginType.BRUTE,
            montant=marge,
            pourcentage=pourcentage,
            base_calcul=chiffre_affaires,
            details={
                "formule": "CA - Coût de revient",
                "cout_revient": cout_revient
            }
        )
    
    @staticmethod
    def calculer_marge_nette(
        marge_brute: float,
        charges: float
    ) -> MarginResult:
        """
        Calculer la marge nette
        
        Args:
            marge_brute: Marge brute
            charges: Charges (frais généraux, administratifs, etc.)
        
        Returns:
            MarginResult: Marge nette calculée
        """
        marge = marge_brute - charges
        base = marge_brute + charges if (marge_brute + charges) > 0 else 1
        pourcentage = (marge / base * 100) if base > 0 else 0
        
        return MarginResult(
            type=MarginType.NETTE,
            montant=marge,
            pourcentage=pourcentage,
            base_calcul=base,
            details={
                "formule": "Marge brute - Charges",
                "charges": charges
            }
        )
    
    @staticmethod
    def calculer_marge_commerciale(
        chiffre_affaires: float,
        coefficient_vente: float = 1.20
    ) -> MarginResult:
        """
        Calculer la marge commerciale
        
        Args:
            chiffre_affaires: Chiffre d'affaires HT
            coefficient_vente: Coefficient de vente appliqué
        
        Returns:
            MarginResult: Marge commerciale calculée
        """
        # La marge commerciale est la différence entre le prix de vente et le coût d'achat
        # Avec un coefficient, on peut calculer: CA * (coeff - 1)
        marge = chiffre_affaires * (coefficient_vente - 1)
        pourcentage = ((coefficient_vente - 1) * 100) if coefficient_vente > 0 else 0
        
        return MarginResult(
            type=MarginType.COMMERCIALE,
            montant=marge,
            pourcentage=pourcentage,
            base_calcul=chiffre_affaires,
            details={
                "formule": "CA * (coeff_vente - 1)",
                "coefficient_vente": coefficient_vente
            }
        )
    
    @staticmethod
    def calculer_marge_cible(
        chiffre_affaires: float,
        marge_cible_pourcentage: float = 10.0
    ) -> MarginResult:
        """
        Calculer la marge cible
        
        Args:
            chiffre_affaires: Chiffre d'affaires HT
            marge_cible_pourcentage: Pourcentage de marge cible
        
        Returns:
            MarginResult: Marge cible calculée
        """
        marge = chiffre_affaires * (marge_cible_pourcentage / 100)
        
        return MarginResult(
            type=MarginType.CIBLE,
            montant=marge,
            pourcentage=marge_cible_pourcentage,
            base_calcul=chiffre_affaires,
            details={
                "formule": "CA * (pourcentage_cible / 100)",
                "pourcentage_cible": marge_cible_pourcentage
            }
        )


# =============================================================================
# CALCULATEUR PRINCIPAL
# =============================================================================

class MarginAnalyzer:
    """
    Analyseur complet des marges et coefficients
    """
    
    def __init__(self):
        self.coefficient_calculator = CoefficientCalculator()
        self.margin_calculator = MarginCalculator()
    
    def analyser(
        self,
        chiffre_affaires: float,
        cout_revient: float,
        charges: float = 0.0,
        coefficient_vente: Optional[float] = None,
        marge_cible_pourcentage: Optional[float] = None
    ) -> MarginAnalysis:
        """
        Analyser complètement les marges
        
        Args:
            chiffre_affaires: Chiffre d'affaires HT
            cout_revient: Coût de revient total
            charges: Charges supplémentaires
            coefficient_vente: Coefficient de vente personnalisé
            marge_cible_pourcentage: Pourcentage de marge cible
        
        Returns:
            MarginAnalysis: Analyse complète des marges
        """
        # Calculer les coefficients
        coefficients = self.coefficient_calculator.calculer_tous()
        
        # Appliquer le coefficient de vente personnalisé
        if coefficient_vente is not None:
            coefficients[CoefficientType.VENTE.value] = self.coefficient_calculator.calculer(
                CoefficientType.VENTE, coefficient_vente
            )
        
        # Calculer les marges
        marge_brute = self.margin_calculator.calculer_marge_brute(
            chiffre_affaires, cout_revient
        )
        
        marge_nette = self.margin_calculator.calculer_marge_nette(
            marge_brute.montant, charges
        )
        
        coeff_vente = coefficients[CoefficientType.VENTE.value].valeur
        marge_commerciale = self.margin_calculator.calculer_marge_commerciale(
            chiffre_affaires, coeff_vente
        )
        
        # Calculer la marge cible
        marge_cible = None
        if marge_cible_pourcentage is not None:
            marge_cible = self.margin_calculator.calculer_marge_cible(
                chiffre_affaires, marge_cible_pourcentage
            )
        
        # Calculer l'écart vs cible
        ecart_vs_cible = 0.0
        if marge_cible:
            ecart_vs_cible = marge_nette.montant - marge_cible.montant
        
        # Déterminer le niveau de risque
        niveau_risque = self._determiner_niveau_risque(marge_nette.pourcentage, ecart_vs_cible)
        
        return MarginAnalysis(
            marge_brute=marge_brute,
            marge_nette=marge_nette,
            marge_commerciale=marge_commerciale,
            coefficients=coefficients,
            marge_cible=marge_cible,
            ecart_vs_cible=ecart_vs_cible,
            niveau_risque=niveau_risque
        )
    
    def _determiner_niveau_risque(
        self,
        marge_nette_pourcentage: float,
        ecart_vs_cible: float
    ) -> str:
        """
        Déterminer le niveau de risque basé sur la marge
        
        Args:
            marge_nette_pourcentage: Pourcentage de marge nette
            ecart_vs_cible: Écart par rapport à la marge cible
        
        Returns:
            str: Niveau de risque (FAIBLE, MOYEN, ELEVE, CRITIQUE)
        """
        # Niveau basé sur la marge nette
        if marge_nette_pourcentage < 0:
            return "CRITIQUE"  # Perte
        elif marge_nette_pourcentage < 5:
            return "ELEVE"  # Marge trop faible
        elif marge_nette_pourcentage < 10:
            return "MOYEN"  # Marge acceptable mais serrée
        
        # Niveau basé sur l'écart vs cible
        if ecart_vs_cible < 0:
            # En dessous de la cible
            if abs(ecart_vs_cible) > marge_nette_pourcentage * 0.5:
                return "ELEVE"
        
        return "FAIBLE"  # Marge saine


# =============================================================================
# UTILITIES
# =============================================================================

def calculer_marge_nette(
    chiffre_affaires: float,
    cout_revient: float,
    charges: float = 0.0
) -> float:
    """
    Calculer la marge nette rapidement
    
    Args:
        chiffre_affaires: Chiffre d'affaires HT
        cout_revient: Coût de revient
        charges: Charges supplémentaires
    
    Returns:
        float: Marge nette en EUR
    """
    return chiffre_affaires - cout_revient - charges


def calculer_marge_pourcentage(
    chiffre_affaires: float,
    cout_revient: float
) -> float:
    """
    Calculer le pourcentage de marge brute
    
    Args:
        chiffre_affaires: Chiffre d'affaires HT
        cout_revient: Coût de revient
    
    Returns:
        float: Pourcentage de marge brute
    """
    if chiffre_affaires == 0:
        return 0.0
    return ((chiffre_affaires - cout_revient) / chiffre_affaires) * 100


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

margin_analyzer = MarginAnalyzer()


def get_margin_analyzer() -> MarginAnalyzer:
    """Get the singleton MarginAnalyzer instance"""
    return margin_analyzer
