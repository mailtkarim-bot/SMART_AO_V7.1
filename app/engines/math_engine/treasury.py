"""
SMART_AO V7 - treasury.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Treasury Calculator
==================================
Calcul déterministe de la trésorerie et des flux financiers
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

class FluxType(str, Enum):
    """Type de flux financier"""
    ENCAISSEMENT = "encaissement"
    DECAISSEMENT = "decaisement"


class AvanceType(str, Enum):
    """Type d'avance"""
    AVANCE_2024 = "avance_2024"  # 30% État, 10% collectivités > 60 M€
    ACONTE = "acompte"
    SITUATION = "situation"


class TypeAcheteur(str, Enum):
    """Type d'acheteur public (impacte le taux d'avance)."""
    ETAT = "etat"                         # État et opérateurs de l'État
    COLLECTIVITE = "collectivite"         # Collectivités territoriales
    AUTRE = "autre"                       # Autres organismes publics


# =============================================================================\n# DATA CLASSES
# =============================================================================

@dataclass
class FluxTresorerie:
    """Un flux de trésorerie"""
    date: date
    montant: float
    type: FluxType
    libelle: str
    echeance: Optional[int] = None  # Jours à partir de la date de début


@dataclass
class AvanceCalculee:
    """Résultat du calcul d'une avance"""
    type: AvanceType
    montant: float
    pourcentage: float
    base_calcul: float
    date_versement: Optional[date] = None
    conditions: Optional[List[str]] = None


@dataclass
class BFRResult:
    """Résultat du calcul du BFR"""
    bfr_total: float
    bfr_par_mois: Dict[str, float]
    bfr_cumul: Dict[str, float]
    pic_bfr: float
    mois_pic: str
    besoins_financement: float


@dataclass
class TreasuryAnalysis:
    """Analyse complète de trésorerie"""
    avance: AvanceCalculee
    bfr: BFRResult
    flux_tresorerie: List[FluxTresorerie]
    solde_tresorerie: Dict[str, float]  # Solde par mois
    solde_minimal: float
    mois_critique: str
    recommandations: List[str]


# =============================================================================
# CALCULATEUR D'AVANCES
# =============================================================================

class AvanceCalculator:
    """
    Calculateur des avances selon les règles du BTP
    
    Règles 2024 (P0):
    - Avance standard: 30% du montant HT
    - Avance réduite: 10% du montant HT (pour marchés spécifiques)
    - Acompte: 10-20% du montant HT
    
    Conditions typiques:
    - Fournir une caution bancaire
    - Justifier de la capacité financière
    - Respecter les délais de versement
    """
    
    # Pourcentages par défaut
    POURCENTAGES = {
        AvanceType.AVANCE_2024: 30.0,  # 30% par défaut (État)
        AvanceType.ACONTE: 15.0,       # 15% par défaut
        AvanceType.SITUATION: 10.0     # 10% par défaut
    }

    # Seuil pour l'avance réduite des collectivités (en EUR)
    SEUIL_COLLECTIVITE_AVANCE_REDUIT = 60_000_000.0

    @staticmethod
    def _pourcentage_avance_2024(
        type_acheteur: TypeAcheteur,
        montant_marche_ht: float,
        pourcentage_override: Optional[float]
    ) -> float:
        """
        Déterminer le pourcentage d'avance selon l'acheteur public.

        Règles 2024:
        - État / opérateurs de l'État : 30%.
        - Collectivités territoriales pour marchés > 60 M€ HT : 10%.
        - Autres cas : pas d'avance légale automatique (0%, acompte possible).
        """
        if pourcentage_override is not None:
            return pourcentage_override

        if type_acheteur == TypeAcheteur.ETAT:
            return 30.0

        if (
            type_acheteur == TypeAcheteur.COLLECTIVITE
            and montant_marche_ht > AvanceCalculator.SEUIL_COLLECTIVITE_AVANCE_REDUIT
        ):
            return 10.0

        # Aucun taux légal automatique pour les autres cas.
        return 0.0

    @staticmethod
    def calculer(
        montant_marche_ht: float,
        avance_type: AvanceType = AvanceType.AVANCE_2024,
        pourcentage: Optional[float] = None,
        date_debut: Optional[date] = None,
        delai_versement_jours: int = 30,
        type_acheteur: TypeAcheteur = TypeAcheteur.ETAT
    ) -> AvanceCalculee:
        """
        Calculer une avance.

        Args:
            montant_marche_ht: Montant du marché HT (EUR).
            avance_type: Type d'avance.
            pourcentage: Pourcentage personnalisé (optionnel).
            date_debut: Date de début du marché.
            delai_versement_jours: Délai de versement en jours.
            type_acheteur: Type d'acheteur public (détermine le taux légal 2024).

        Returns:
            AvanceCalculee: Résultat du calcul.
        """
        # Déterminer le pourcentage
        if pourcentage is not None:
            pourcentage_applique = pourcentage
        elif avance_type == AvanceType.AVANCE_2024:
            pourcentage_applique = AvanceCalculator._pourcentage_avance_2024(
                type_acheteur, montant_marche_ht, None
            )
        else:
            pourcentage_applique = AvanceCalculator.POURCENTAGES.get(
                avance_type, 0.0
            )

        # Calculer le montant
        montant = montant_marche_ht * (pourcentage_applique / 100)

        # Calculer la date de versement
        date_versement = None
        if date_debut:
            date_versement = date_debut + timedelta(days=delai_versement_jours)

        # Conditions par défaut
        conditions = [
            "Fournir une caution bancaire",
            "Justifier de la capacité financière",
            f"Respecter délai de versement: {delai_versement_jours} jours"
        ]

        # Ajouter des conditions spécifiques selon le type
        if avance_type == AvanceType.AVANCE_2024:
            conditions.append("Marché public conforme au code des marchés publics")
            if type_acheteur == TypeAcheteur.ETAT:
                conditions.append("Avance légale État / opérateur de l'État: 30%")
            elif type_acheteur == TypeAcheteur.COLLECTIVITE:
                if montant_marche_ht > AvanceCalculator.SEUIL_COLLECTIVITE_AVANCE_REDUIT:
                    conditions.append(
                        f"Collectivité > {AvanceCalculator.SEUIL_COLLECTIVITE_AVANCE_REDUIT:,.0f} EUR HT: avance réduite 10%"
                    )
                else:
                    conditions.append("Collectivité <= seuil: aucune avance légale automatique")

        return AvanceCalculee(
            type=avance_type,
            montant=montant,
            pourcentage=pourcentage_applique,
            base_calcul=montant_marche_ht,
            date_versement=date_versement,
            conditions=conditions
        )


# =============================================================================
# CALCULATEUR DE BFR (BESOIN EN FONDS DE ROULEMENT)
# =============================================================================

class BFRCalculator:
    """
    Calculateur du Besoin en Fonds de Roulement
    
    Formule BTP standard:
    BFR = (Stocks + Créances clients) - (Dettes fournisseurs + Dettes fiscales)
    
    Pour un marché:
    - Stocks: matériaux, équipements sur site
    - Créances clients: factures non payées
    - Dettes fournisseurs: délais de paiement fournisseurs
    - Dettes fiscales: TVA à payer, etc.
    """
    
    @staticmethod
    def calculer_par_mois(
        planning: Dict[str, Dict[str, float]],
        couts_materiaux: Dict[str, float],
        delai_paiement_clients: int = 60,
        delai_paiement_fournisseurs: int = 30
    ) -> BFRResult:
        """
        Calculer le BFR par mois
        
        Args:
            planning: Planning des travaux par mois {mois: {type: montant}}
            couts_materiaux: Coûts des matériaux par mois
            delai_paiement_clients: Délai de paiement clients (jours)
            delai_paiement_fournisseurs: Délai de paiement fournisseurs (jours)
        
        Returns:
            BFRResult: Résultat du calcul
        """
        bfr_par_mois = {}
        bfr_cumul = {}
        solde_cumul = 0.0
        
        # Convertir les délais en mois pour simplification
        delai_clients_mois = delai_paiement_clients / 30
        delai_fournisseurs_mois = delai_paiement_fournisseurs / 30
        
        # Trier les mois par ordre chronologique
        mois_ordres = sorted(planning.keys())
        
        for mois in mois_ordres:
            mois_data = planning.get(mois, {})
            
            # Coûts du mois (sorties de trésorerie)
            cout_materiaux = couts_materiaux.get(mois, 0)
            main_doeuvre = mois_data.get("main_doeuvre", 0)
            sous_traitance = mois_data.get("sous_traitance", 0)
            autres_couts = mois_data.get("autres", 0)
            
            total_sorties = cout_materiaux + main_doeuvre + sous_traitance + autres_couts
            
            # Facturation du mois (entrées de trésorerie)
            facturation = mois_data.get("facturation", 0)
            
            # Calcul des créances (facturation non encaissée)
            # On considère que le paiement intervient après delai_clients_mois
            # Pour le mois courant, on ajoute à la créance
            # Pour les mois passés, on soustrait ce qui est encaissé
            
            # Simplification: BFR = Créances - Dettes
            # Créances = facturation * delai_clients_mois / 30
            # Dettes = (cout_materiaux + main_doeuvre) * delai_fournisseurs_mois / 30
            
            creances = facturation * (delai_clients_mois / 30)
            dettes_fournisseurs = (cout_materiaux + main_doeuvre + sous_traitance) * (delai_fournisseurs_mois / 30)
            
            # BFR du mois
            bfr_mois = creances - dettes_fournisseurs
            bfr_par_mois[mois] = bfr_mois
            
            # BFR cumulé
            solde_cumul += bfr_mois
            bfr_cumul[mois] = solde_cumul
        
        # Trouver le pic de BFR
        pic_bfr = max(bfr_cumul.values()) if bfr_cumul else 0.0
        mois_pic = max(bfr_cumul, key=bfr_cumul.get) if bfr_cumul else ""
        
        # Besoin de financement = Pic de BFR (si positif)
        besoins_financement = max(0, pic_bfr)
        
        return BFRResult(
            bfr_total=bfr_cumul.get(mois_pic, 0.0),
            bfr_par_mois=bfr_par_mois,
            bfr_cumul=bfr_cumul,
            pic_bfr=pic_bfr,
            mois_pic=mois_pic,
            besoins_financement=besoins_financement
        )
    
    @staticmethod
    def calculer_simple(
        chiffre_affaires_annuel: float,
        cout_revient_annuel: float,
        delai_paiement_clients: int = 60,
        delai_paiement_fournisseurs: int = 30,
        stock_moyen: float = 0.0
    ) -> float:
        """
        Calculer le BFR de manière simplifiée
        
        Formule: BFR = (CA * delai_clients/360) + Stocks - (Couts * delai_fournisseurs/360)
        
        Args:
            chiffre_affaires_annuel: CA annuel (EUR)
            cout_revient_annuel: Coût de revient annuel (EUR)
            delai_paiement_clients: Délai de paiement clients (jours)
            delai_paiement_fournisseurs: Délai de paiement fournisseurs (jours)
            stock_moyen: Stock moyen (EUR)
        
        Returns:
            float: BFR moyen (EUR)
        """
        # Créances clients
        creances = chiffre_affaires_annuel * (delai_paiement_clients / 360)
        
        # Dettes fournisseurs
        dettes_fournisseurs = cout_revient_annuel * (delai_paiement_fournisseurs / 360)
        
        # BFR
        bfr = creances + stock_moyen - dettes_fournisseurs
        
        return round(bfr, 2)


# =============================================================================
# CALCULATEUR DE FLUX DE TRÉSORERIE
# =============================================================================

class FluxTresorerieCalculator:
    """
    Calculateur des flux de trésorerie
    
    Génère les flux mensuels de trésorerie pour un marché
    """
    
    @staticmethod
    def generer_flux(
        planning: Dict[str, Dict[str, float]],
        avance: AvanceCalculee,
        bfr_result: BFRResult,
        date_debut: date,
        duree_mois: int
    ) -> List[FluxTresorerie]:
        """
        Générer les flux de trésorerie mensuels
        
        Args:
            planning: Planning des travaux
            avance: Avance reçue
            bfr_result: Résultat BFR
            date_debut: Date de début
            duree_mois: Durée en mois
        
        Returns:
            List[FluxTresorerie]: Liste des flux
        """
        flux = []
        
        # Ajouter l'avance comme premier flux
        flux.append(FluxTresorerie(
            date=avance.date_versement if avance.date_versement else date_debut,
            montant=avance.montant,
            type=FluxType.ENCAISSEMENT,
            libelle="Avance marché",
            echeance=0
        ))
        
        # Générer les flux mensuels
        for i in range(1, duree_mois + 1):
            mois = f"M{i:02d}"
            date_mois = date_debut + timedelta(days=30 * i)
            
            mois_data = planning.get(mois, {})
            
            # Facturation (encaissement)
            facturation = mois_data.get("facturation", 0)
            if facturation > 0:
                flux.append(FluxTresorerie(
                    date=date_mois,
                    montant=facturation,
                    type=FluxType.ENCAISSEMENT,
                    libelle=f"Facturation {mois}",
                    echeance=i * 30
                ))
            
            # Coûts (décaisements)
            cout_materiaux = mois_data.get("materiaux", 0)
            main_doeuvre = mois_data.get("main_doeuvre", 0)
            sous_traitance = mois_data.get("sous_traitance", 0)
            
            total_couts = cout_materiaux + main_doeuvre + sous_traitance
            if total_couts > 0:
                flux.append(FluxTresorerie(
                    date=date_debut + timedelta(days=30 * (i - 1) + 15),  # Milieu du mois précédent
                    montant=-total_couts,
                    type=FluxType.DECAISSEMENT,
                    libelle=f"Coûts {mois}",
                    echeance=(i - 1) * 30 + 15
                ))
        
        # Solde final (règlement final)
        solde_final = mois_data.get("solde", 0) if mois_data else 0
        if solde_final > 0:
            flux.append(FluxTresorerie(
                date=date_debut + timedelta(days=30 * duree_mois + 30),
                montant=solde_final,
                type=FluxType.ENCAISSEMENT,
                libelle="Solde final",
                echeance=30 * (duree_mois + 1)
            ))
        
        # Trier par date
        flux.sort(key=lambda x: x.date if x.date else date.min)
        
        return flux


# =============================================================================
# ANALYSEUR DE TRÉSORERIE PRINCIPAL
# =============================================================================

class TreasuryAnalyzer:
    """
    Analyseur complet de trésorerie
    
    Combine:
    - Calcul des avances
    - Calcul du BFR
    - Génération des flux
    - Analyse du solde minimal
    """
    
    def __init__(self):
        self.avance_calculator = AvanceCalculator()
        self.bfr_calculator = BFRCalculator()
        self.flux_calculator = FluxTresorerieCalculator()
    
    def analyser(
        self,
        montant_marche_ht: float,
        planning: Dict[str, Dict[str, float]],
        couts_materiaux: Dict[str, float],
        date_debut: date,
        delai_paiement_clients: int = 60,
        delai_paiement_fournisseurs: int = 30,
        pourcentage_avance: Optional[float] = None,
        type_acheteur: TypeAcheteur = TypeAcheteur.ETAT
    ) -> TreasuryAnalysis:
        """
        Analyser complètement la trésorerie d'un marché.

        Args:
            montant_marche_ht: Montant du marché HT (EUR).
            planning: Planning des travaux par mois.
            couts_materiaux: Coûts des matériaux par mois.
            date_debut: Date de début du marché.
            delai_paiement_clients: Délai de paiement clients (jours).
            delai_paiement_fournisseurs: Délai de paiement fournisseurs (jours).
            pourcentage_avance: Pourcentage d'avance personnalisé (optionnel).
            type_acheteur: Type d'acheteur public (détermine le taux légal 2024).

        Returns:
            TreasuryAnalysis: Analyse complète.
        """
        # Calculer l'avance
        avance = self.avance_calculator.calculer(
            montant_marche_ht,
            AvanceType.AVANCE_2024,
            pourcentage_avance,
            date_debut,
            type_acheteur=type_acheteur
        )
        
        # Calculer le BFR
        bfr = self.bfr_calculator.calculer_par_mois(
            planning, couts_materiaux, 
            delai_paiement_clients, delai_paiement_fournisseurs
        )
        
        # Générer les flux de trésorerie
        duree_mois = len(planning)
        flux_tresorerie = self.flux_calculator.generer_flux(
            planning, avance, bfr, date_debut, duree_mois
        )
        
        # Calculer le solde de trésorerie par mois
        solde_tresorerie = self._calculer_solde_tresorerie(
            flux_tresorerie, avance.montant, date_debut
        )
        
        # Trouver le solde minimal
        solde_minimal = min(solde_tresorerie.values()) if solde_tresorerie else 0.0
        mois_critique = min(solde_tresorerie, key=solde_tresorerie.get) if solde_tresorerie else ""
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(
            solde_minimal, avance.montant, bfr.pic_bfr
        )
        
        return TreasuryAnalysis(
            avance=avance,
            bfr=bfr,
            flux_tresorerie=flux_tresorerie,
            solde_tresorerie=solde_tresorerie,
            solde_minimal=solde_minimal,
            mois_critique=mois_critique,
            recommandations=recommandations
        )
    
    def _calculer_solde_tresorerie(
        self,
        flux: List[FluxTresorerie],
        avance_initiale: float,
        date_debut: date
    ) -> Dict[str, float]:
        """
        Calculer le solde de trésorerie par mois
        
        Args:
            flux: Liste des flux
            avance_initiale: Montant de l'avance initiale
            date_debut: Date de début
        
        Returns:
            Dict[str, float]: Solde par mois
        """
        solde_tresorerie = {}
        solde = avance_initiale
        
        # Regrouper par mois
        flux_par_mois = {}
        for f in flux:
            if f.date:
                mois_key = f"M{(f.date.year - date_debut.year) * 12 + (f.date.month - date_debut.month) + 1:02d}"
                if mois_key not in flux_par_mois:
                    flux_par_mois[mois_key] = []
                flux_par_mois[mois_key].append(f)
        
        # Calculer le solde pour chaque mois
        mois_ordres = sorted(flux_par_mois.keys())
        for mois in mois_ordres:
            flux_mois = flux_par_mois[mois]
            for f in flux_mois:
                solde += f.montant
            
            solde_tresorerie[mois] = solde
        
        return solde_tresorerie
    
    def _generer_recommandations(
        self,
        solde_minimal: float,
        avance: float,
        pic_bfr: float
    ) -> List[str]:
        """
        Générer des recommandations basé sur l'analyse
        
        Args:
            solde_minimal: Solde minimal atteint
            avance: Montant de l'avance
            pic_bfr: Pic de BFR
        
        Returns:
            List[str]: Liste des recommandations
        """
        recommandations = []
        
        if solde_minimal < 0:
            recommandations.append(
                f"DÉFICIT DE TRÉSORERIE: Solde minimal de {solde_minimal:.2f}€. "
                f"Prévoir un financement complémentaire de {-solde_minimal:.2f}€"
            )
        
        if pic_bfr > avance * 0.8:
            recommandations.append(
                f"BFR ÉLEVÉ: Pic de {pic_bfr:.2f}€ > 80% de l'avance ({avance * 0.8:.2f}€). "
                "Négocier un délai de paiement client plus court ou une avance complémentaire"
            )
        
        if pic_bfr > 0:
            recommandations.append(
                f"Besoin de financement BFR: {pic_bfr:.2f}€. "
                "Vérifier que la trésorerie disponible couvre ce besoin"
            )
        
        return recommandations


# =============================================================================
# UTILITIES
# =============================================================================

def calculer_avance(montant_ht: float, pourcentage: float = 30.0) -> float:
    """Calculer rapidement le montant d'une avance"""
    return montant_ht * (pourcentage / 100)


def calculer_bfr_simple(
    ca_annuel: float,
    couts_annuels: float,
    delai_clients: int = 60,
    delai_fournisseurs: int = 30
) -> float:
    """Calculer rapidement le BFR"""
    return BFRCalculator.calculer_simple(
        ca_annuel, couts_annuels, delai_clients, delai_fournisseurs
    )


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

treasury_analyzer = TreasuryAnalyzer()


def get_treasury_analyzer() -> TreasuryAnalyzer:
    """Get the singleton TreasuryAnalyzer instance"""
    return treasury_analyzer
