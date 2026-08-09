"""
SMART_AO V7 - risques_generator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Génération des Risques Chantier - Identification et analyse des risques BTP
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from datetime import datetime, date
import logging
from enum import Enum

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


class NiveauRisque(Enum):
    """Niveaux de risque BTP."""
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class TypeRisque(Enum):
    """Types de risques en construction."""
    TECHNIQUE = "technique"
    FINANCIER = "financier"
    REGLEMENTAIRE = "reglementaire"
    SECURITE = "securite"
    ENVIRONNEMENTAL = "environnemental"
    ORGANISATIONNEL = "organisationnel"
    JURIDIQUE = "juridique"


@dataclass
class Risque:
    """Représente un risque identifié."""
    risque_id: str
    nom: str
    description: str
    type_risque: str
    niveau: str
    probabilite: float
    impact: Decimal
    mission_id: Optional[str] = None
    lot_concerne: Optional[str] = None
    date_identification: date = field(default_factory=date.today)
    mitigation: Optional[str] = None
    responsable: Optional[str] = None
    
    def score_risque(self) -> float:
        """Calcule le score de risque (probabilité * impact normalisé)."""
        impact_normalise = min(float(self.impact) / Decimal("1000000"), 1.0) if self.impact > 0 else 0
        return self.probabilite * impact_normalise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "risque_id": self.risque_id,
            "nom": self.nom,
            "description": self.description,
            "type_risque": self.type_risque,
            "niveau": self.niveau,
            "probabilite": self.probabilite,
            "impact": float(self.impact),
            "score": self.score_risque(),
            "mission_id": self.mission_id,
            "lot_concerne": self.lot_concerne,
            "date_identification": self.date_identification.isoformat(),
            "mitigation": self.mitigation,
            "responsable": self.responsable
        }


@dataclass
class CategorieRisque:
    """Catégorie de risques."""
    categorie_id: str
    nom: str
    description: str
    poids: float = 1.0
    risques: List[Risque] = field(default_factory=list)
    
    def risque_max(self) -> Optional[Risque]:
        """Retourne le risque avec le score le plus élevé."""
        if not self.risques:
            return None
        return max(self.risques, key=lambda r: r.score_risque())
    
    def score_moyen(self) -> float:
        """Score moyen de la catégorie."""
        if not self.risques:
            return 0.0
        return sum(r.score_risque() for r in self.risques) / len(self.risques)


@dataclass
class AnalyseRisque:
    """Résultat complet d'une analyse de risques."""
    analyse_id: str
    mission_id: str
    date_analyse: date
    categories: List[CategorieRisque] = field(default_factory=list)
    risques_totaux: int = 0
    risques_critiques: int = 0
    risques_eleves: int = 0
    score_global: float = 0.0
    niveau_global: str = "faible"
    recommandations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "analyse_id": self.analyse_id,
            "mission_id": self.mission_id,
            "date_analyse": self.date_analyse.isoformat(),
            "risques_totaux": self.risques_totaux,
            "risques_critiques": self.risques_critiques,
            "risques_eleves": self.risques_eleves,
            "score_global": self.score_global,
            "niveau_global": self.niveau_global,
            "recommandations": self.recommandations,
            "categories": [
                {
                    "categorie_id": c.categorie_id,
                    "nom": c.nom,
                    "score_moyen": c.score_moyen(),
                    "nb_risques": len(c.risques),
                    "risque_max": c.risque_max().to_dict() if c.risque_max() else None
                }
                for c in self.categories
            ]
        }


@dataclass
class MatriceRisque:
    """Matrice de risque pour visualisation."""
    mission_id: str
    matrice: Dict[str, Dict[str, int]] = field(default_factory=dict)
    seuils: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        self.seuils = {
            "faible": (0.0, 0.3),
            "moyen": (0.3, 0.6),
            "eleve": (0.6, 0.8),
            "critique": (0.8, 1.0)
        }


class RisquesGenerator:
    """
    Générateur et analyseur de risques chantier.
    
    Identifie, catégorise et priorise les risques BTP selon la méthodologie
    SMART_AO V7 avec intégration des référentiels métiers.
    """
    
    BASE_RISQUES_TECHNIQUES = [
        {
            "id": "RISQUE_SOL_INSTABLE",
            "nom": "Sol instable ou pollué",
            "description": "Présence de sol instable, argileux ou pollué nécessitant des fondations spécifiques",
            "type": "technique",
            "niveau": "eleve",
            "probabilite": 0.3,
            "impact": Decimal("500000"),
            "mitigation": "Étude géotechnique approfondie (G2 minimum), fondations adaptées"
        },
        {
            "id": "RISQUE_STRUCTURE_COMPLEXE",
            "nom": "Structure porteuse complexe",
            "description": "Conception structurelle complexe avec risques de calculs erronés",
            "type": "technique",
            "niveau": "moyen",
            "probabilite": 0.25,
            "impact": Decimal("300000"),
            "mitigation": "Vérification par bureau de contrôle agréé"
        },
        {
            "id": "RISQUE_ACCESSIBILITE_CHANTIER",
            "nom": "Accès difficile au chantier",
            "description": "Site avec accès restreint pour les engins et matériaux",
            "type": "technique",
            "niveau": "moyen",
            "probabilite": 0.4,
            "impact": Decimal("150000"),
            "mitigation": "Plan de logistique détaillé, phasage adapté"
        }
    ]
    
    BASE_RISQUES_FINANCIERS = [
        {
            "id": "RISQUE_HAUSSE_MATERIAUX",
            "nom": "Hausse des prix des matériaux",
            "description": "Volatilité des prix des matériaux de construction (+15% à +30% en 2026)",
            "type": "financier",
            "niveau": "eleve",
            "probabilite": 0.7,
            "impact": Decimal("250000"),
            "mitigation": "Clauses d'indexation dans les contrats, achats groupés"
        },
        {
            "id": "RISQUE_RETARD_PAIEMENT",
            "nom": "Retard de paiement client",
            "description": "Retard de paiement du maître d'ouvrage ou maître d'œuvre",
            "type": "financier",
            "niveau": "critique",
            "probabilite": 0.35,
            "impact": Decimal("500000"),
            "mitigation": "Garantie de paiement, pénalties de retard"
        },
        {
            "id": "RISQUE_DEPASSEMENT_BUDGET",
            "nom": "Dépassement du budget prévisionnel",
            "description": "Risque de dépassement du budget initial de plus de 10%",
            "type": "financier",
            "niveau": "eleve",
            "probabilite": 0.45,
            "impact": Decimal("400000"),
            "mitigation": "Suivi mensuel des coûts, provision pour aléas"
        }
    ]
    
    BASE_RISQUES_REGLEMENTAIRES = [
        {
            "id": "RISQUE_RE2020",
            "nom": "Non-conformité RE2020",
            "description": "Risque de non-respect des exigences de la réglementation environnementale",
            "type": "reglementaire",
            "niveau": "critique",
            "probabilite": 0.25,
            "impact": Decimal("1000000"),
            "mitigation": "Audit RE2020 en amont, concertation avec bureau d'études thermique"
        },
        {
            "id": "RISQUE_ACCESSIBILITE_PMR",
            "nom": "Non-conformité accessibilité PMR",
            "description": "Risque de non-conformité aux normes d'accessibilité",
            "type": "reglementaire",
            "niveau": "eleve",
            "probabilite": 0.2,
            "impact": Decimal("200000"),
            "mitigation": "Vérification par contrôleur technique agréé"
        },
        {
            "id": "RISQUE_DT_DICT",
            "nom": "Retard dans les DT/DICT",
            "description": "Retard dans l'obtention des déclarations préalables ou autorisations",
            "type": "reglementaire",
            "niveau": "moyen",
            "probabilite": 0.5,
            "impact": Decimal("100000"),
            "mitigation": "Dépôt des dossiers avec anticipation, suivi rapproché"
        }
    ]
    
    BASE_RISQUES_SECURITE = [
        {
            "id": "RISQUE_CHUTE_HAUTEUR",
            "nom": "Chute de hauteur",
            "description": "Risque d'accident du travail par chute de hauteur",
            "type": "securite",
            "niveau": "critique",
            "probabilite": 0.15,
            "impact": Decimal("2000000"),
            "mitigation": "Échafaudages conformes, EPI, formation sécurité"
        },
        {
            "id": "RISQUE_MANUTENTION",
            "nom": "Risque de manutention manuelle",
            "description": "TMS (Troubles Musculo-Squelettiques) liés à la manutention",
            "type": "securite",
            "niveau": "eleve",
            "probabilite": 0.4,
            "impact": Decimal("500000"),
            "mitigation": "Utilisation d'engins de levage, formation gestuelle"
        },
        {
            "id": "RISQUE_COACTIVITE",
            "nom": "Risque de coactivité",
            "description": "Présence de plusieurs entreprises sur le même chantier",
            "type": "securite",
            "niveau": "moyen",
            "probabilite": 0.3,
            "impact": Decimal("300000"),
            "mitigation": "Plan de prévention, coordination SPS"
        }
    ]
    
    BASE_RISQUES_ENVIRONNEMENTAUX = [
        {
            "id": "RISQUE_DECHETS_AMIANTE",
            "nom": "Présence d'amiante",
            "description": "Découverte d'amiante lors des travaux de démolition ou rénovation",
            "type": "environnemental",
            "niveau": "critique",
            "probabilite": 0.2,
            "impact": Decimal("800000"),
            "mitigation": "Diagnostic amiante préalable, désamiantage par entreprise certifiée"
        },
        {
            "id": "RISQUE_POLLUTION_SOL",
            "nom": "Pollution du sol",
            "description": "Découverte de pollution du sol non identifiée en amont",
            "type": "environnemental",
            "niveau": "eleve",
            "probabilite": 0.15,
            "impact": Decimal("600000"),
            "mitigation": "Étude des sols (phase 2 minimum), dépollution si nécessaire"
        },
        {
            "id": "RISQUE_NUISANCES_VOISINAGE",
            "nom": "Nuisances pour le voisinage",
            "description": "Bruit, poussière ou vibrations affectant les riverains",
            "type": "environnemental",
            "niveau": "moyen",
            "probabilite": 0.35,
            "impact": Decimal("100000"),
            "mitigation": "Mesures de mitigation (écrans, horaires adaptés), communication"
        }
    ]
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
        self.base_risques = self._charger_base_risques()
    
    def _charger_base_risques(self) -> Dict[str, List[Dict[str, Any]]]:
        """Charge la base de connaissances des risques."""
        return {
            "techniques": self.BASE_RISQUES_TECHNIQUES,
            "financiers": self.BASE_RISQUES_FINANCIERS,
            "reglementaires": self.BASE_RISQUES_REGLEMENTAIRES,
            "securite": self.BASE_RISQUES_SECURITE,
            "environnementaux": self.BASE_RISQUES_ENVIRONNEMENTAUX
        }
    
    def _creer_risque(self, data: Dict[str, Any], mission_id: Optional[str] = None, 
                     lot: Optional[str] = None) -> Risque:
        """Crée un objet Risque à partir de données."""
        return Risque(
            risque_id=data["id"],
            nom=data["nom"],
            description=data["description"],
            type_risque=data["type"],
            niveau=data["niveau"],
            probabilite=data["probabilite"],
            impact=Decimal(str(data["impact"])),
            mission_id=mission_id,
            lot_concerne=lot,
            mitigation=data.get("mitigation")
        )
    
    def analyser_risques_projet(
        self,
        mission_id: str,
        type_projet: str,
        lot: Optional[str] = None,
        montants: Optional[Dict[str, Decimal]] = None,
        delai: Optional[int] = None
    ) -> AnalyseRisque:
        """
        Analyse complète des risques pour un projet.
        
        Args:
            mission_id: ID de la mission
            type_projet: Type de projet
            lot: Lot spécifique concerné
            montants: Dictionnaire des montants
            delai: Délai du projet en jours
            
        Returns:
            AnalyseRisque complète
        """
        logger.info(f"Analyse des risques pour mission {mission_id} - type: {type_projet}")
        
        categories = []
        tous_risques = []
        poids_par_type = self._get_poids_par_type_projet(type_projet)
        
        for type_risque, risques_data in self.base_risques.items():
            categorie_risques = []
            
            for risque_data in risques_data:
                ajustement = poids_par_type.get(type_risque, 1.0)
                risque = self._creer_risque(risque_data, mission_id, lot)
                risque.probabilite = min(risque.probabilite * ajustement, 0.95)
                
                if montants and type_risque == "financier":
                    budget = montants.get("budget", Decimal("1000000"))
                    impact_ratio = min(float(budget) / 1000000, 3.0)
                    risque.impact = risque.impact * Decimal(str(impact_ratio))
                
                if type_risque == "technique" and delai:
                    delai_ratio = min(delai / 365, 2.0)
                    risque.impact = risque.impact * Decimal(str(1 + delai_ratio * 0.5))
                
                categorie_risques.append(risque)
                tous_risques.append(risque)
            
            categories.append(CategorieRisque(
                categorie_id=f"CAT_{type_risque}_{mission_id}",
                nom=type_risque.title(),
                description=f"Risques {type_risque} pour la mission {mission_id}",
                poids=poids_par_type.get(type_risque, 1.0),
                risques=categorie_risques
            ))
        
        risques_critiques = sum(1 for r in tous_risques if r.niveau == "critique")
        risques_eleves = sum(1 for r in tous_risques if r.niveau == "eleve")
        score_global = sum(r.score_risque() for r in tous_risques) / len(tous_risques) if tous_risques else 0.0
        niveau_global = self._determiner_niveau_global(score_global, risques_critiques)
        recommandations = self._generer_recommandations(categories, score_global)
        
        analyse_id = f"ANALYSE_RISQUE-{mission_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return AnalyseRisque(
            analyse_id=analyse_id,
            mission_id=mission_id,
            date_analyse=date.today(),
            categories=categories,
            risques_totaux=len(tous_risques),
            risques_critiques=risques_critiques,
            risques_eleves=risques_eleves,
            score_global=round(score_global, 4),
            niveau_global=niveau_global,
            recommandations=recommandations
        )
    
    def _get_poids_par_type_projet(self, type_projet: str) -> Dict[str, float]:
        """Retourne les poids d'ajustement par type de risque selon le type de projet."""
        poids = {
            "neuf": {"technique": 1.1, "reglementaire": 1.2, "environnemental": 0.9, "securite": 1.0, "financier": 1.0},
            "renovation": {"technique": 1.3, "reglementaire": 1.1, "environnemental": 1.5, "securite": 1.2, "financier": 1.1},
            "reabilitation": {"technique": 1.2, "reglementaire": 1.3, "environnemental": 1.4, "securite": 1.1, "financier": 1.0},
            "demolition": {"technique": 0.8, "reglementaire": 1.0, "environnemental": 1.8, "securite": 1.5, "financier": 0.9}
        }
        return poids.get(type_projet, poids["neuf"])
    
    def _determiner_niveau_global(self, score: float, nb_critiques: int) -> str:
        """Détermine le niveau global de risque."""
        if nb_critiques >= 3:
            return "critique"
        if nb_critiques >= 1 or score >= 0.7:
            return "eleve"
        if score >= 0.4:
            return "moyen"
        return "faible"
    
    def _generer_recommandations(self, categories: List[CategorieRisque], score_global: float) -> List[str]:
        """Génère des recommandations basées sur l'analyse."""
        recommandations = []
        
        for categorie in categories:
            if categorie.score_moyen() >= 0.7:
                recommandations.append(f"Priorité absolue à la gestion des risques {categorie.nom.lower()}")
            elif categorie.score_moyen() >= 0.4:
                recommandations.append(f"Surveillance renforcée des risques {categorie.nom.lower()}")
        
        if score_global >= 0.7:
            recommandations.insert(0, "Mettre en place un comité de pilotage risque hebdomadaire")
            recommandations.append("Prevoir un budget de provision pour aleas de 10-15%")
        elif score_global >= 0.4:
            recommandations.insert(0, "Revue mensuelle des risques avec l'équipe projet")
        
        if any(c.nom == "environnemental" for c in categories):
            recommandations.append("Verifier la conformite des diagnostics amiante et pollution")
        
        if any(c.nom == "reglementaire" for c in categories):
            recommandations.append("S'assurer de la complete des dossiers administratifs")
        
        return list(set(recommandations))
    
    def generer_matrice_risque(self, mission_id: str, risques: List[Risque]) -> MatriceRisque:
        """Génère une matrice de risque."""
        matrice = MatriceRisque(mission_id=mission_id)
        
        for risque in risques:
            niveau_proba = self._categoriser_probabilite(risque.probabilite)
            niveau_impact = self._categoriser_impact(risque.impact)
            
            if niveau_proba not in matrice.matrice:
                matrice.matrice[niveau_proba] = {}
            if niveau_impact not in matrice.matrice[niveau_proba]:
                matrice.matrice[niveau_proba][niveau_impact] = 0
            matrice.matrice[niveau_proba][niveau_impact] += 1
        
        return matrice
    
    def _categoriser_probabilite(self, probabilite: float) -> str:
        """Catégorise la probabilité."""
        if probabilite >= 0.7:
            return "elevee"
        elif probabilite >= 0.4:
            return "moyenne"
        elif probabilite >= 0.1:
            return "faible"
        return "tres_faible"
    
    def _categoriser_impact(self, impact: Decimal) -> str:
        """Catégorise l'impact."""
        impact_float = float(impact)
        if impact_float >= 500000:
            return "catastrophique"
        elif impact_float >= 200000:
            return "majeur"
        elif impact_float >= 50000:
            return "significatif"
        elif impact_float >= 10000:
            return "mineur"
        return "negligeable"
    
    def identifier_risques_lot(self, mission_id: str, lot: str, caracteristiques: Dict[str, Any]) -> List[Risque]:
        """Identifie les risques spécifiques à un lot."""
        logger.info(f"Identification des risques pour lot {lot} - mission {mission_id}")
        
        risques_lot = {
            "gros_oeuvre": [
                {"id": f"RISQUE_GO_{mission_id}_001", "nom": "Erreur de fondations", "description": "Risque de dimensionnement incorrect des fondations", "type": "technique", "niveau": "critique", "probabilite": 0.2, "impact": Decimal("800000"), "mitigation": "Verification par geotechnicien et bureau de controle"},
                {"id": f"RISQUE_GO_{mission_id}_002", "nom": "Retard livraison beton", "description": "Retard dans la livraison du beton arme", "type": "organisationnel", "niveau": "moyen", "probabilite": 0.35, "impact": Decimal("120000"), "mitigation": "Contrats avec plusieurs fournisseurs"}
            ],
            "second_oeuvre": [
                {"id": f"RISQUE_SO_{mission_id}_001", "nom": "Non-conformite menuiseries", "description": "Menuiseries non conformes aux exigences", "type": "technique", "niveau": "moyen", "probabilite": 0.25, "impact": Decimal("80000"), "mitigation": "Pre-validation des echantillons"},
                {"id": f"RISQUE_SO_{mission_id}_002", "nom": "Retard approvisionnement", "description": "Retard dans l'approvisionnement", "type": "organisationnel", "niveau": "moyen", "probabilite": 0.4, "impact": Decimal("60000"), "mitigation": "Commandes anticipees"}
            ],
            "electricite": [
                {"id": f"RISQUE_ELEC_{mission_id}_001", "nom": "Risque electrique", "description": "Risque d'electrocution ou d'incendie", "type": "securite", "niveau": "critique", "probabilite": 0.15, "impact": Decimal("1500000"), "mitigation": "Installation par entreprise qualifiee"}
            ],
            "cvc": [
                {"id": f"RISQUE_CVC_{mission_id}_001", "nom": "Fuite reseau", "description": "Risque de fuite sur les reseaux", "type": "technique", "niveau": "eleve", "probabilite": 0.2, "impact": Decimal("150000"), "mitigation": "Tests d'etancheite systematiques"}
            ]
        }
        
        risques_specifics = risques_lot.get(lot, [])
        return [self._creer_risque(r, mission_id, lot) for r in risques_specifics]
    
    def prioriser_risques(self, risques: List[Risque]) -> List[Risque]:
        """Priorise les risques par score décroissant."""
        return sorted(risques, key=lambda r: r.score_risque(), reverse=True)


generator = RisquesGenerator()


def analyser_risques_mission(mission_id: str, type_projet: str, lot: Optional[str] = None, montants: Optional[Dict[str, Any]] = None, delai: Optional[int] = None) -> Dict[str, Any]:
    """Analyse complete des risques pour une mission."""
    analyse = generator.analyser_risques_projet(mission_id, type_projet, lot, montants, delai)
    return analyse.to_dict()


def identifier_risques_lot_api(mission_id: str, lot: str, caracteristiques: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identifie les risques pour un lot specifique."""
    risques = generator.identifier_risques_lot(mission_id, lot, caracteristiques)
    return [r.to_dict() for r in risques]


def prioriser_risques_api(risques_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Priorise une liste de risques."""
    risques = [Risque(risque_id=r["risque_id"], nom=r["nom"], description=r["description"], type_risque=r["type_risque"], niveau=r["niveau"], probabilite=r["probabilite"], impact=Decimal(str(r["impact"])), mission_id=r.get("mission_id"), lot_concerne=r.get("lot_concerne"), mitigation=r.get("mitigation")) for r in risques_data]
    priorises = generator.prioriser_risques(risques)
    return [r.to_dict() for r in priorises]


def generer_matrice_risque_api(mission_id: str, risques_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genere une matrice de risque."""
    risques = [Risque(risque_id=r["risque_id"], nom=r["nom"], description=r["description"], type_risque=r["type_risque"], niveau=r["niveau"], probabilite=r["probabilite"], impact=Decimal(str(r["impact"]))) for r in risques_data]
    matrice = generator.generer_matrice_risque(mission_id, risques)
    return {"mission_id": matrice.mission_id, "matrice": {proba: {imp: count for imp, count in data.items()} for proba, data in matrice.matrice.items()}, "seuils": matrice.seuils}


