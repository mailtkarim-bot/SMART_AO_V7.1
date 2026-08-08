"""
SMART_AO V7 - mapa_generator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - MAPA Generator
============================
Génération de Marchés à Procédure Adaptée (MAPA)
Détection et génération des documents MAPA selon le Code des Marchés Publics

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


# Seuil MAPA 2024 (selon Code des Marchés Publics)
SEUIL_MAPA_ETAT = 40000  # € HT pour l'État
SEUIL_MAPA_COLLECTIVITES = 40000  # € HT pour les collectivités territoriales
SEUIL_MAPA_HOPITAUX = 80000  # € HT pour les hôpitaux


@dataclass
class MAPA:
    """Représente un Marché à Procédure Adaptée."""
    reference: str
    objet: str
    montant_ht: float
    montant_tva: float
    montant_ttc: float
    duree_mois: int
    date_notification: Optional[date] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    acheteur: str = ""
    type_acheteur: str = "ETAT"  # ETAT, COLLECTIVITE, HOPITAL
    
    @property
    def est_mapa(self) -> bool:
        """Vérifier si le marché est un MAPA."""
        if self.type_acheteur == "HOPITAL":
            return self.montant_ht < SEUIL_MAPA_HOPITAUX
        else:
            return self.montant_ht < SEUIL_MAPA_ETAT
    
    @property
    def seuil_applicable(self) -> float:
        """Récupérer le seuil applicable selon le type d'acheteur."""
        if self.type_acheteur == "HOPITAL":
            return SEUIL_MAPA_HOPITAUX
        else:
            return SEUIL_MAPA_ETAT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "reference": self.reference,
            "objet": self.objet,
            "montant_ht": round(self.montant_ht, 2),
            "montant_tva": round(self.montant_tva, 2),
            "montant_ttc": round(self.montant_ttc, 2),
            "duree_mois": self.duree_mois,
            "date_notification": self.date_notification.isoformat() if self.date_notification else None,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "acheteur": self.acheteur,
            "type_acheteur": self.type_acheteur,
            "est_mapa": self.est_mapa,
            "seuil_applicable": self.seuil_applicable
        }


@dataclass
class MAPAAnalysis:
    """Analyse MAPA complète."""
    est_mapa: bool
    montant_ht: float
    seuil_applicable: float
    type_acheteur: str
    ecart_au_seuil: float = 0.0
    recommandations: List[str] = None
    
    def __post_init__(self):
        if self.recommandations is None:
            self.recommandations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "est_mapa": self.est_mapa,
            "montant_ht": round(self.montant_ht, 2),
            "seuil_applicable": self.seuil_applicable,
            "type_acheteur": self.type_acheteur,
            "ecart_au_seuil": round(self.ecart_au_seuil, 2),
            "recommandations": self.recommandations
        }


class MAPAGenerator:
    """
    Générateur et analyseur de MAPA (Marchés à Procédure Adaptée).
    
    Fonctionnalités:
    - Détecter si un marché est un MAPA
    - Générer les documents nécessaires pour un MAPA
    - Vérifier la conformité réglementaire
    - Calculer les seuils et recommandations
    """
    
    def __init__(self):
        self.mapa: Optional[MAPA] = None
        self.analysis: Optional[MAPAAnalysis] = None
    
    def analyser_marche(
        self,
        montant_ht: float,
        type_acheteur: str = "ETAT",
        acheteur: str = ""
    ) -> MAPAAnalysis:
        """
        Analyser si un marché est un MAPA et générer des recommandations.
        
        Args:
            montant_ht: Montant HT du marché (€)
            type_acheteur: Type d'acheteur (ETAT, COLLECTIVITE, HOPITAL)
            acheteur: Nom de l'acheteur
        
        Returns:
            MAPAAnalysis: Analyse complète
        """
        # Déterminer le seuil applicable
        if type_acheteur == "HOPITAL":
            seuil = SEUIL_MAPA_HOPITAUX
        else:
            seuil = SEUIL_MAPA_ETAT
        
        est_mapa = montant_ht < seuil
        ecart = seuil - montant_ht if est_mapa else montant_ht - seuil
        
        # Générer des recommandations
        recommandations = []
        
        if est_mapa:
            recommandations.append(
                f"✅ Marché éligible à la procédure adaptée (MAPA) "
                f"- Montant: {montant_ht:.2f} € < {seuil:.2f} €"
            )
            recommandations.append(
                "📋 Documents requis: Devis signés, conditions de paiement, "
                "délais d'exécution, pénalités de retard"
            )
            recommandations.append(
                "⏱️ Délai minimum: 11 jours (vs 21 jours pour les marchés formalisés)"
            )
        else:
            recommandations.append(
                f"❌ Marché NON éligible à la MAPA - Montant: {montant_ht:.2f} € > {seuil:.2f} €"
            )
            recommandations.append(
                "⚠️ Procédure formalisée obligatoire (appel d'offres ouvert/restreint)"
            )
            recommandations.append(
                f"💡 Pour devenir MAPA: diviser le marché en lots < {seuil:.2f} €"
            )
        
        # Recommandations spécifiques selon l'acheteur
        if type_acheteur == "HOPITAL":
            recommandations.append(
                "ℹ️ Pour les hôpitaux: seuil MAPA = 80 000 € (vs 40 000 € pour l'État)"
            )
        
        # Vérifier si proche du seuil
        if abs(ecart) < seuil * 0.10:  # Dans les 10% du seuil
            recommandations.append(
                f"⚠️ Attention: montant proche du seuil ({abs(ecart)/seuil*100:.1f}% d'écart)"
            )
            if not est_mapa:
                recommandations.append(
                    "💡 Conseillé: négocier pour réduire le montant et passer en MAPA"
                )
        
        self.analysis = MAPAAnalysis(
            est_mapa=est_mapa,
            montant_ht=montant_ht,
            seuil_applicable=seuil,
            type_acheteur=type_acheteur,
            ecart_au_seuil=ecart,
            recommandations=recommandations
        )
        
        return self.analysis
    
    def generer_mapa(
        self,
        reference: str,
        objet: str,
        montant_ht: float,
        duree_mois: int,
        type_acheteur: str = "ETAT",
        acheteur: str = "",
        date_notification: Optional[date] = None
    ) -> MAPA:
        """
        Générer un objet MAPA complet.
        
        Args:
            reference: Référence du marché
            objet: Objet du marché
            montant_ht: Montant HT (€)
            duree_mois: Durée en mois
            type_acheteur: Type d'acheteur
            acheteur: Nom de l'acheteur
            date_notification: Date de notification
        
        Returns:
            MAPA: L'objet MAPA généré
        """
        tva = montant_ht * 0.20  # TVA standard 20%
        montant_ttc = montant_ht + tva
        
        if date_notification is None:
            date_notification = date.today()
        
        date_debut = date_notification + timedelta(days=14)  # 14 jours pour commencer
        date_fin = date_debut + timedelta(days=30 * duree_mois)
        
        self.mapa = MAPA(
            reference=reference,
            objet=objet,
            montant_ht=montant_ht,
            montant_tva=tva,
            montant_ttc=montant_ttc,
            duree_mois=duree_mois,
            date_notification=date_notification,
            date_debut=date_debut,
            date_fin=date_fin,
            acheteur=acheteur,
            type_acheteur=type_acheteur
        )
        
        return self.mapa
    
    def generer_devis_mapa(
        self,
        entreprise: str,
        siret: str,
        adresse: str,
        montant_ht: float,
        duree_mois: int,
        objet: str,
        reference: str
    ) -> Dict[str, Any]:
        """
        Générer un devis type pour un MAPA.
        
        Args:
            entreprise: Nom de l'entreprise
            siret: SIRET de l'entreprise
            adresse: Adresse de l'entreprise
            montant_ht: Montant HT (€)
            duree_mois: Durée en mois
            objet: Objet du marché
            reference: Référence du marché
        
        Returns:
            Dict: Devis au format dictionnaire
        """
        tva = montant_ht * 0.20
        montant_ttc = montant_ht + tva
        
        devis = {
            "entreprise": {
                "nom": entreprise,
                "siret": siret,
                "adresse": adresse
            },
            "marche": {
                "reference": reference,
                "objet": objet,
                "type": "MAPA",
                "seuil": self.analysis.seuil_applicable if self.analysis else SEUIL_MAPA_ETAT
            },
            "financier": {
                "montant_ht": round(montant_ht, 2),
                "tva": round(tva, 2),
                "taux_tva": "20%",
                "montant_ttc": round(montant_ttc, 2)
            },
            "duree": {
                "mois": duree_mois,
                "jours": duree_mois * 30
            },
            "conditions": {
                "paiement": "30% à la signature, 70% à la réception",
                "delai_execution": f"{duree_mois} mois",
                "penalites": "10% du montant pour retard > 30 jours (CCAG)"
            },
            "date_etablissement": date.today().isoformat(),
            "validite": 30  # Validité en jours
        }
        
        return devis


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def est_mapa(montant_ht: float, type_acheteur: str = "ETAT") -> bool:
    """
    Vérifier rapidement si un montant est éligible à la MAPA.
    
    Args:
        montant_ht: Montant HT (€)
        type_acheteur: Type d'acheteur
    
    Returns:
        bool: True si éligible à la MAPA
    """
    generator = MAPAGenerator()
    analysis = generator.analyser_marche(montant_ht, type_acheteur)
    return analysis.est_mapa


def analyser_mapa(
    montant_ht: float,
    type_acheteur: str = "ETAT"
) -> Dict[str, Any]:
    """
    Analyser un marché pour la conformité MAPA.
    
    Args:
        montant_ht: Montant HT (€)
        type_acheteur: Type d'acheteur
    
    Returns:
        Analyse MAPA au format dictionnaire
    """
    generator = MAPAGenerator()
    analysis = generator.analyser_marche(montant_ht, type_acheteur)
    return analysis.to_dict()


def generer_devis_mapa(
    entreprise: str,
    siret: str,
    adresse: str,
    montant_ht: float,
    duree_mois: int,
    objet: str,
    reference: str,
    type_acheteur: str = "ETAT"
) -> Dict[str, Any]:
    """
    Générer un devis MAPA.
    
    Args:
        Voir la méthode generer_devis_mapa de MAPAGenerator
    
    Returns:
        Devis MAPA au format dictionnaire
    """
    generator = MAPAGenerator()
    return generator.generer_devis_mapa(
        entreprise, siret, adresse, montant_ht, duree_mois, objet, reference
    )


if __name__ == "__main__":
    # Exemple d'utilisation
    generator = MAPAGenerator()
    
    # Analyser un marché de 35k€ pour l'État
    print("Analyse MAPA - État - 35 000 €:")
    analysis = generator.analyser_marche(35000, "ETAT")
    print(f"Est MAPA: {analysis.est_mapa}")
    print(f"Seuil: {analysis.seuil_applicable} €")
    print(f"Recommandations: {analysis.recommandations}")
    
    print("\n" + "="*50 + "\n")
    
    # Analyser un marché de 50k€ pour l'État
    print("Analyse MAPA - État - 50 000 €:")
    analysis = generator.analyser_marche(50000, "ETAT")
    print(f"Est MAPA: {analysis.est_mapa}")
    print(f"Seuil: {analysis.seuil_applicable} €")
    print(f"Recommandations: {analysis.recommandations}")
    
    print("\n" + "="*50 + "\n")
    
    # Analyser un marché de 75k€ pour un hôpital
    print("Analyse MAPA - Hôpital - 75 000 €:")
    analysis = generator.analyser_marche(75000, "HOPITAL")
    print(f"Est MAPA: {analysis.est_mapa}")
    print(f"Seuil: {analysis.seuil_applicable} €")
    print(f"Recommandations: {analysis.recommandations}")

