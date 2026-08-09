"""
SMART_AO V7 - site_coeff.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Coefficients Site - Calcul des coefficients multiplicateurs liés au site
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
import logging

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


@dataclass
class CoefficientSite:
    """Représente un coefficient multiplicateur lié au site."""
    code: str
    nom: str
    categorie: str
    valeur: Decimal
    description: str
    unite: Optional[str] = None
    min_valeur: Optional[Decimal] = None
    max_valeur: Optional[Decimal] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "code": self.code,
            "nom": self.nom,
            "categorie": self.categorie,
            "valeur": float(self.valeur),
            "description": self.description,
            "unite": self.unite,
            "min_valeur": float(self.min_valeur) if self.min_valeur else None,
            "max_valeur": float(self.max_valeur) if self.max_valeur else None
        }


@dataclass
class CategorieCoefficient:
    """Catégorie de coefficients."""
    categorie_id: str
    nom: str
    description: str
    coefficients: List[CoefficientSite] = field(default_factory=list)
    poids: float = 1.0
    
    def get_coefficient(self, code: str) -> Optional[CoefficientSite]:
        """Récupère un coefficient par son code."""
        for coeff in self.coefficients:
            if coeff.code == code:
                return coeff
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "categorie_id": self.categorie_id,
            "nom": self.nom,
            "description": self.description,
            "poids": self.poids,
            "coefficients": [c.to_dict() for c in self.coefficients]
        }


@dataclass
class CalculCoefficients:
    """Résultat du calcul des coefficients pour un site."""
    site_id: str
    mission_id: str
    coefficients_appliques: List[CoefficientSite]
    coefficient_global: Decimal
    details: Dict[str, Any]
    recommandations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "site_id": self.site_id,
            "mission_id": self.mission_id,
            "coefficient_global": float(self.coefficient_global),
            "coefficients_appliques": [c.to_dict() for c in self.coefficients_appliques],
            "details": self.details,
            "recommandations": self.recommandations
        }


class SiteCoeffCalculator:
    """
    Calculateur de coefficients site pour l'estimation des coûts et délais.
    
    Calcule les coefficients multiplicateurs liés aux contraintes spécifiques
    du site (accès, topographie, réglementation locale, etc.).
    """
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
        self.categories = self._init_categories()
    
    def _init_categories(self) -> Dict[str, CategorieCoefficient]:
        """Initialise les catégories de coefficients."""
        return {
            "acces": CategorieCoefficient(
                categorie_id="CAT_ACCES",
                nom="Accès au site",
                description="Coefficients liés aux contraintes d'accès",
                poids=1.2,
                coefficients=self._init_coeffs_acces()
            ),
            "topographie": CategorieCoefficient(
                categorie_id="CAT_TOPO",
                nom="Topographie",
                description="Coefficients liés à la topographie du site",
                poids=1.1,
                coefficients=self._init_coeffs_topographie()
            ),
            "reglementation": CategorieCoefficient(
                categorie_id="CAT_REGLEM",
                nom="Réglementation locale",
                description="Coefficients liés aux contraintes réglementaires locales",
                poids=1.3,
                coefficients=self._init_coeffs_reglementation()
            ),
            "environnement": CategorieCoefficient(
                categorie_id="CAT_ENV",
                nom="Environnement",
                description="Coefficients liés aux contraintes environnementales",
                poids=1.0,
                coefficients=self._init_coeffs_environnement()
            ),
            "logistique": CategorieCoefficient(
                categorie_id="CAT_LOG",
                nom="Logistique",
                description="Coefficients liés à la logistique du chantier",
                poids=0.9,
                coefficients=self._init_coeffs_logistique()
            )
        }
    
    def _init_coeffs_acces(self) -> List[CoefficientSite]:
        """Initialise les coefficients d'accès."""
        return [
            CoefficientSite(
                code="ACCES_FACILE",
                nom="Accès facile",
                categorie="acces",
                valeur=Decimal("1.00"),
                description="Site avec accès direct pour tous les engins",
                min_valeur=Decimal("1.00"),
                max_valeur=Decimal("1.00")
            ),
            CoefficientSite(
                code="ACCES_RESTREINT",
                nom="Accès restreint",
                categorie="acces",
                valeur=Decimal("1.15"),
                description="Site avec accès limité nécessitant des manoeuvres",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.20")
            ),
            CoefficientSite(
                code="ACCES_DIFFICILE",
                nom="Accès difficile",
                categorie="acces",
                valeur=Decimal("1.35"),
                description="Site avec accès très difficile (rues étroites, virages serrés)",
                min_valeur=Decimal("1.30"),
                max_valeur=Decimal("1.50")
            ),
            CoefficientSite(
                code="ACCES_IMPOSSIBLE_ENGINS",
                nom="Accès impossible pour engins",
                categorie="acces",
                valeur=Decimal("1.80"),
                description="Site inaccessible pour les engins, nécessité de grue ou transport manuel",
                min_valeur=Decimal("1.70"),
                max_valeur=Decimal("2.20")
            ),
            CoefficientSite(
                code="ACCES_PEAGE",
                nom="Accès avec péage",
                categorie="acces",
                valeur=Decimal("1.05"),
                description="Site nécessitant le passage par des routes à péage",
                min_valeur=Decimal("1.05"),
                max_valeur=Decimal("1.10")
            )
        ]
    
    def _init_coeffs_topographie(self) -> List[CoefficientSite]:
        """Initialise les coefficients de topographie."""
        return [
            CoefficientSite(
                code="TOPO_PLAT",
                nom="Terrain plat",
                categorie="topographie",
                valeur=Decimal("1.00"),
                description="Terrain parfaitement plat",
                min_valeur=Decimal("1.00"),
                max_valeur=Decimal("1.00")
            ),
            CoefficientSite(
                code="TOPO_LEGER_PENTE",
                nom="Légère pente",
                categorie="topographie",
                valeur=Decimal("1.05"),
                description="Terrain avec pente faible (< 5%)",
                min_valeur=Decimal("1.02"),
                max_valeur=Decimal("1.08")
            ),
            CoefficientSite(
                code="TOPO_PENTE_MOYENNE",
                nom="Pente moyenne",
                categorie="topographie",
                valeur=Decimal("1.15"),
                description="Terrain avec pente moyenne (5-15%)",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.20")
            ),
            CoefficientSite(
                code="TOPO_PENTE_FORTE",
                nom="Forte pente",
                categorie="topographie",
                valeur=Decimal("1.30"),
                description="Terrain avec forte pente (> 15%)",
                min_valeur=Decimal("1.25"),
                max_valeur=Decimal("1.40")
            ),
            CoefficientSite(
                code="TOPO_ESCARPE",
                nom="Terrain en escarpement",
                categorie="topographie",
                valeur=Decimal("1.50"),
                description="Terrain avec dénivelé important, nécessitant terrassement spécifique",
                min_valeur=Decimal("1.40"),
                max_valeur=Decimal("1.70")
            ),
            CoefficientSite(
                code="TOPO_MARAIS",
                nom="Terrain marécageux",
                categorie="topographie",
                valeur=Decimal("1.45"),
                description="Terrain humide ou marécageux nécessitant des fondations spéciales",
                min_valeur=Decimal("1.40"),
                max_valeur=Decimal("1.60")
            )
        ]
    
    def _init_coeffs_reglementation(self) -> List[CoefficientSite]:
        """Initialise les coefficients de réglementation."""
        return [
            CoefficientSite(
                code="REGLEM_STANDARD",
                nom="Réglementation standard",
                categorie="reglementation",
                valeur=Decimal("1.00"),
                description="Zone soumise à la réglementation standard",
                min_valeur=Decimal("1.00"),
                max_valeur=Decimal("1.00")
            ),
            CoefficientSite(
                code="REGLEM_SECTEUR_PROTEGE",
                nom="Secteur protégé",
                categorie="reglementation",
                valeur=Decimal("1.25"),
                description="Zone classée (ABF, monument historique, site naturel)",
                min_valeur=Decimal("1.20"),
                max_valeur=Decimal("1.40")
            ),
            CoefficientSite(
                code="REGLEM_ZONE_URBAINE",
                nom="Zone urbaine dense",
                categorie="reglementation",
                valeur=Decimal("1.15"),
                description="Zone urbaine avec contraintes (bruit, horaires, circulation)",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.20")
            ),
            CoefficientSite(
                code="REGLEM_PPR",
                nom="Plan de Prévention des Risques",
                categorie="reglementation",
                valeur=Decimal("1.20"),
                description="Zone soumise à PPR (inondation, mouvement de terrain, etc.)",
                min_valeur=Decimal("1.15"),
                max_valeur=Decimal("1.30")
            ),
            CoefficientSite(
                code="REGLEM_BATIMENT_EXISTANT",
                nom="Bâtiment existant",
                categorie="reglementation",
                valeur=Decimal("1.10"),
                description="Travaux en site occupé ou sur bâtiment existant",
                min_valeur=Decimal("1.05"),
                max_valeur=Decimal("1.15")
            ),
            CoefficientSite(
                code="REGLEM_HAUTEUR",
                nom="Contrainte de hauteur",
                categorie="reglementation",
                valeur=Decimal("1.12"),
                description="Contraintes de hauteur (PLU, COS, etc.)",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.15")
            )
        ]
    
    def _init_coeffs_environnement(self) -> List[CoefficientSite]:
        """Initialise les coefficients environnementaux."""
        return [
            CoefficientSite(
                code="ENV_NEUTRE",
                nom="Impact environnemental neutre",
                categorie="environnement",
                valeur=Decimal("1.00"),
                description="Site sans contrainte environnementale particulière",
                min_valeur=Decimal("1.00"),
                max_valeur=Decimal("1.00")
            ),
            CoefficientSite(
                code="ENV_AMIANTE",
                nom="Présence d'amiante",
                categorie="environnement",
                valeur=Decimal("1.40"),
                description="Site avec présence d'amiante nécessitant désamiantage",
                min_valeur=Decimal("1.35"),
                max_valeur=Decimal("1.50")
            ),
            CoefficientSite(
                code="ENV_POLLUTION_SOL",
                nom="Sol pollué",
                categorie="environnement",
                valeur=Decimal("1.35"),
                description="Site avec sol pollué nécessitant dépollution",
                min_valeur=Decimal("1.30"),
                max_valeur=Decimal("1.45")
            ),
            CoefficientSite(
                code="ENV_ZONE_HUMIDE",
                nom="Zone humide",
                categorie="environnement",
                valeur=Decimal("1.25"),
                description="Site en zone humide (loi sur l'eau)",
                min_valeur=Decimal("1.20"),
                max_valeur=Decimal("1.35")
            ),
            CoefficientSite(
                code="ENV_ESPECE_PROTEGEE",
                nom="Espèce protégée",
                categorie="environnement",
                valeur=Decimal("1.30"),
                description="Présence d'espèce protégée nécessitant mesures compensatoires",
                min_valeur=Decimal("1.25"),
                max_valeur=Decimal("1.40")
            ),
            CoefficientSite(
                code="ENV_NUISANCES",
                nom="Contrainte de nuisances",
                categorie="environnement",
                valeur=Decimal("1.08"),
                description="Site avec contraintes de bruit, poussière ou vibrations",
                min_valeur=Decimal("1.05"),
                max_valeur=Decimal("1.15")
            )
        ]
    
    def _init_coeffs_logistique(self) -> List[CoefficientSite]:
        """Initialise les coefficients de logistique."""
        return [
            CoefficientSite(
                code="LOG_STANDARD",
                nom="Logistique standard",
                categorie="logistique",
                valeur=Decimal("1.00"),
                description="Site avec logistique standard",
                min_valeur=Decimal("1.00"),
                max_valeur=Decimal("1.00")
            ),
            CoefficientSite(
                code="LOG_ELOIGNE",
                nom="Site éloigné",
                categorie="logistique",
                valeur=Decimal("1.12"),
                description="Site éloigné (> 50 km des fournisseurs)",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.15")
            ),
            CoefficientSite(
                code="LOG_IMPORT",
                nom="Matériaux importés",
                categorie="logistique",
                valeur=Decimal("1.18"),
                description="Nécéssité de matériaux importés avec délais d'approvisionnement longs",
                min_valeur=Decimal("1.15"),
                max_valeur=Decimal("1.25")
            ),
            CoefficientSite(
                code="LOG_STOCKAGE_LIMITÉ",
                nom="Stockage limité",
                categorie="logistique",
                valeur=Decimal("1.10"),
                description="Site avec espace de stockage limité",
                min_valeur=Decimal("1.08"),
                max_valeur=Decimal("1.15")
            ),
            CoefficientSite(
                code="LOG_ZONE_URBAINE",
                nom="Livraison en zone urbaine",
                categorie="logistique",
                valeur=Decimal("1.15"),
                description="Difficulté de livraison en zone urbaine dense",
                min_valeur=Decimal("1.10"),
                max_valeur=Decimal("1.20")
            ),
            CoefficientSite(
                code="LOG_PENALITES_RETARD",
                nom="Pénalités de retard",
                categorie="logistique",
                valeur=Decimal("1.05"),
                description="Contrat avec pénalités de retard élevées",
                min_valeur=Decimal("1.05"),
                max_valeur=Decimal("1.10")
            )
        ]
    
    def get_coefficient(self, code: str) -> Optional[CoefficientSite]:
        """Récupère un coefficient par son code."""
        for categorie in self.categories.values():
            coeff = categorie.get_coefficient(code)
            if coeff:
                return coeff
        return None
    
    def get_coefficients_by_categorie(self, categorie: str) -> Optional[CategorieCoefficient]:
        """Récupère une catégorie de coefficients."""
        return self.categories.get(categorie)
    
    def calculer_coefficient_site(
        self,
        site_id: str,
        mission_id: str,
        codes_coeffs: List[str],
        apply_min_max: bool = True
    ) -> CalculCoefficients:
        """
        Calcule le coefficient global pour un site.
        
        Args:
            site_id: ID du site
            mission_id: ID de la mission
            codes_coeffs: Liste des codes de coefficients à appliquer
            apply_min_max: Si True, applique les contraintes min/max
            
        Returns:
            CalculCoefficients
        """
        logger.info(f"Calcul des coefficients pour site {site_id} - mission {mission_id}")
        
        coefficients_appliques = []
        produits = Decimal("1.00")
        details = {}
        
        for code in codes_coeffs:
            coeff = self.get_coefficient(code)
            if coeff:
                coefficients_appliques.append(coeff)
                
                # Appliquer min/max si activé
                valeur = coeff.valeur
                if apply_min_max:
                    if coeff.min_valeur and valeur < coeff.min_valeur:
                        valeur = coeff.min_valeur
                    if coeff.max_valeur and valeur > coeff.max_valeur:
                        valeur = coeff.max_valeur
                
                produits *= valeur
                
                details[code] = {
                    "valeur": float(valeur),
                    "categorie": coeff.categorie,
                    "nom": coeff.nom
                }
        
        # Calculer le coefficient pondéré par catégorie
        coeff_pondere = self._calculer_coefficient_pondere(codes_coeffs)
        
        # Générer les recommandations
        recommandations = self._generer_recommandations(coefficients_appliques)
        
        return CalculCoefficients(
            site_id=site_id,
            mission_id=mission_id,
            coefficients_appliques=coefficients_appliques,
            coefficient_global=min(max(produits, Decimal("1.00")), Decimal("3.00")),
            details=details,
            recommandations=recommandations
        )
    
    def _calculer_coefficient_pondere(self, codes_coeffs: List[str]) -> Decimal:
        """Calcule le coefficient pondéré par catégorie."""
        # Grouper les coefficients par catégorie
        categories = {}
        for code in codes_coeffs:
            coeff = self.get_coefficient(code)
            if coeff:
                if coeff.categorie not in categories:
                    categories[coeff.categorie] = []
                categories[coeff.categorie].append(coeff)
        
        # Calculer le produit pondéré
        produit = Decimal("1.00")
        for categorie, coeffs in categories.items():
            cat = self.categories.get(categorie)
            if cat:
                # Produit des coefficients de la catégorie
                prod_cat = Decimal("1.00")
                for c in coeffs:
                    prod_cat *= c.valeur
                # Appliquer le poids de la catégorie
                produit *= prod_cat ** Decimal(str(cat.poids))
        
        return produit
    
    def _generer_recommandations(self, coefficients: List[CoefficientSite]) -> List[str]:
        """Génère des recommandations basées sur les coefficients appliqués."""
        recommandations = []
        
        for coeff in coefficients:
            if coeff.categorie == "acces" and coeff.valeur > Decimal("1.10"):
                recommandations.append("Prevoir un plan de logistique detaille avec etude des acces")
            
            if coeff.categorie == "topographie" and coeff.valeur > Decimal("1.15"):
                recommandations.append("Etude geotechnique approfondie requise")
            
            if coeff.categorie == "reglementation" and coeff.valeur > Decimal("1.20"):
                recommandations.append("Verifier la conformite avec les services urbanisme")
            
            if coeff.categorie == "environnement" and coeff.valeur > Decimal("1.25"):
                recommandations.append("Realiser un diagnostic environnemental complet")
            
            if coeff.categorie == "logistique" and coeff.valeur > Decimal("1.15"):
                recommandations.append("Anticiper les commandes de materiaux")
        
        return list(set(recommandations))
    
    def calculer_coefficient_par_categorie(
        self,
        mission_id: str,
        categorie: str,
        codes_coeffs: List[str]
    ) -> Decimal:
        """
        Calcule le coefficient pour une catégorie spécifique.
        
        Args:
            mission_id: ID de la mission
            categorie: Catégorie de coefficients
            codes_coeffs: Codes des coefficients à appliquer
            
        Returns:
            Coefficient calculé
        """
        cat = self.categories.get(categorie)
        if not cat:
            return Decimal("1.00")
        
        produit = Decimal("1.00")
        for code in codes_coeffs:
            coeff = cat.get_coefficient(code)
            if coeff:
                produit *= coeff.valeur
        
        return produit ** Decimal(str(cat.poids))
    
    def get_all_coefficients(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retourne tous les coefficients disponibles."""
        result = {}
        for cat_id, cat in self.categories.items():
            result[cat_id] = [c.to_dict() for c in cat.coefficients]
        return result


calculator = SiteCoeffCalculator()


def calculer_coefficients_site(
    site_id: str,
    mission_id: str,
    codes_coeffs: List[str]
) -> Dict[str, Any]:
    """Calcule les coefficients pour un site."""
    calcul = calculator.calculer_coefficient_site(site_id, mission_id, codes_coeffs)
    return calcul.to_dict()


def get_coefficient(code: str) -> Optional[Dict[str, Any]]:
    """Recupere un coefficient par son code."""
    coeff = calculator.get_coefficient(code)
    return coeff.to_dict() if coeff else None


def get_all_coefficients() -> Dict[str, List[Dict[str, Any]]]:
    """Recupere tous les coefficients."""
    return calculator.get_all_coefficients()


def calculer_coefficient_par_categorie(
    mission_id: str,
    categorie: str,
    codes_coeffs: List[str]
) -> float:
    """Calcule le coefficient pour une categorie."""
    coeff = calculator.calculer_coefficient_par_categorie(mission_id, categorie, codes_coeffs)
    return float(coeff)


