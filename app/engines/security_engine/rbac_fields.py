"""
SMART_AO V7 - rbac_fields.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - RBAC Sensitive Fields Catalog
============================================
Catalogue canonique des champs sensibles filtrés par le RBAC.

Source: ARCHITECTURE_V7_ENGINE.md §4.2 + ADR-046

Tout champ listé ci-dessous est automatiquement masqué (strip) pour les rôles
non autorisés à accéder aux données financières / stratégiques.
"""

from typing import FrozenSet

# Champs financiers et stratégiques réservés au PATRON / rôles autorisés.
# Catalogue canonical V7.1 — inclut les champs historiques V6 + les nouveaux
# champs V7.1 (pénibilité RH, URSSAF, ZAN, formules de révision, sourcing).
FIELDS_STRIP: FrozenSet[str] = frozenset({
    # Marges et coefficients
    "marge",
    "marges",
    "marge_brute",
    "marge_net",
    "marge_nette",
    "coefficient",
    "coefficients",
    "coefficient_vente",
    "coeff_vente",
    "coefficient_equipement",
    "coeff_equipement",
    "coeff_forfait",
    "markup",

    # Trésorerie et BFR
    "tresorerie",
    "treso",
    "bfr",
    "besoin_fonds_roulement",
    "cash_flow",
    "fonds_roulement",
    "avance_demarrage",
    "avance",
    "accompte",
    "echeancier",
    "paiement",
    "delai_paiement",

    # Coûts, prix et chiffrage
    "prix",
    "prix_unitaire",
    "prix_unitaire_ht",
    "cout",
    "couts",
    "cout_unitaire",
    "cout_direct",
    "cout_indirect",
    "cout_main_oeuvre",
    "cout_materiaux",
    "cout_equipement",
    "cout_sous_traitance",
    "chiffrage",
    "budget",
    "estimation",
    "estimation_interne",
    "montant",
    "montant_ht",
    "montant_ttc",
    "total_ht",
    "total_ttc",
    "valeur",
    "tarif",

    # Pénalités et risques financiers
    "penalite",
    "penalites",
    "retard",
    "penalite_retard",
    "penalites_retard",
    "penalite_cumulee",
    "plafond_penalite",
    "clause_penale",
    "garantie",
    "caution",
    "caution_provisoire",
    "caution_definitive",
    "retenue_garantie",

    # Agrégats financiers
    "financial_data",
    "financial_summary",
    "finance",
    "resultat",
    "resultat_exploitation",
    "revenu",
    "ca",
    "chiffre_affaires",
    "benefice",

    # V7.1 — Pénibilité RH & pénurie main-d'œuvre
    "penibilite",
    "penibilites",
    "surcout_interim",
    "surcout_main_oeuvre",
    "penurie_rh",
    "cout_rh",
    "main_oeuvre",

    # V7.1 — Vigilance URSSAF & délit de marchandage
    "urssaf",
    "attestation_urssaf",
    "delit_marchandage",
    "solidarite",
    "exposition_urssaf",
    "cumul_urssaf",

    # V7.1 — ZAN & Trackterres
    "zan",
    "isdi",
    "trackterres",
    "evacuation",
    "cout_evacuation",
    "terres",
    "zone_action_coeur_ville",

    # V7.1 — Syntax checker formules de révision
    "formule_revision",
    "coefficients_revision",
    "indice_insee",
    "erreur_formule",
    "revision_prix",

    # V7.1 — Sourcing & API Profil Acheteur
    "api_key",
    "api_secret",
    "token_depot",
    "credentials_place",
    "sourcing_cost",
})

# Alias historique pour compatibilité ascendante
FIELDS_STRIP_V6 = FIELDS_STRIP


def is_sensitive_field(field_name: str) -> bool:
    """
    Vérifie si un champ fait partie du catalogue sensible V7.1.

    Args:
        field_name: Nom du champ à vérifier.

    Returns:
        bool: True si le champ doit être masqué par le RBAC.
    """
    return field_name.lower() in FIELDS_STRIP
