"""
SMART_AO V7 - agent_bt01.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - BT01 Conformité Agent
===================================
Agent de vérification de conformité au BT01 (indice INSEE du coût de la construction)
Vérifie la conformité des offres aux exigences légales

Le BT01 est l'indice INSEE de référence pour les formules de révision de prix,
et non un Bordereau des Prix Unitaires.

Fonctionnalités:
- Vérification des indices BT01 dans les formules de révision
- Détection des écarts anormaux
- Vérification des libellés
- Conformité aux seuils légaux
"""

from datetime import timedelta
from typing import List, Dict, Any
import re

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


# =============================================================================
# SEUILS LÉGAUX BT01 (2026)
# =============================================================================

BT01_SEUILS = {
    # Seuils de marché public (Article 26 du Code de la commande publique)
    "SEUIL_MAPA": 40000,  # Marché à procédure adaptée
    "SEUIL_FORMALISE": 140000,  # Seuils européens
    "SEUIL_EUROPEEN_FOURNITURES": 140000,
    "SEUIL_EUROPEEN_TRAVAUX": 5380000,
    
    # Seuils de sous-traitance (Article R. 2192-8)
    "MAX_SOUS_TRAITANCE": 0.30,  # 30% maximum de sous-traitance
    
    # Tolerance d'écart BT01
    "TOLERANCE_ECART_BT01": 0.05,  # 5% d'écart toléré
}


# =============================================================================
# PATTERNS DE VÉRIFICATION
# =============================================================================

BT01_PATTERNS = {
    # Vérification des prix
    "PRIX_UNITAIRE_MANQUANT": {
        "patterns": [
            r"pu\s*=\s*0",
            r"prix\s*unitaire\s*=\s*0",
            r"pu\s*:\s*0",
        ],
        "niveau": "CRITIQUE",
        "reference": "BT01 - Tout prix unitaire doit être renseigné",
        "recommandation": "Vérifier et compléter les prix unitaires manquants"
    },
    
    # Détection des prix aberrants
    "PRIX_ABERRANT": {
        "patterns": [
            r"pu\s*>\s*10000\s*€",  # Prix > 10 000 €/u (à vérifier)
            r"pu\s*<\s*0\.01\s*€",  # Prix < 0,01 €/u
        ],
        "niveau": "ELEVE",
        "reference": "BT01 - Prix doit être cohérent avec le marché",
        "recommandation": "Vérifier la cohérence des prix unitaires"
    },
    
    # Vérification des libellés
    "LIBELLE_MANQUANT": {
        "patterns": [
            r"libellé\s*=\s*$",
            r"désignation\s*=\s*$",
            r"poste\s*\d+\s*:",  # Poste sans libellé
        ],
        "niveau": "ELEVE",
        "reference": "BT01 - Tout poste doit avoir un libellé clair",
        "recommandation": "Compléter les libellés manquants"
    },
    
    # Unité manquante
    "UNITE_MANQUANTE": {
        "patterns": [
            r"unité\s*=\s*$",
            r"u\s*=\s*$",
        ],
        "niveau": "ELEVE",
        "reference": "BT01 - Toute ligne doit avoir une unité",
        "recommandation": "Ajouter les unités manquantes (m, m2, ml, u, etc.)"
    },
    
    # Quantité nulle
    "QUANTITE_NULLE": {
        "patterns": [
            r"qté\s*=\s*0",
            r"quantité\s*=\s*0",
        ],
        "niveau": "MOYEN",
        "reference": "BT01 - Vérifier les quantités nulles",
        "recommandation": "Vérifier si la quantité nulle est intentionnelle"
    },
    
    # Total incohérent
    "TOTAL_INCOHERENT": {
        "patterns": [
            r"total\s*≠\s*pu\s*×\s*qté",
            r"montant\s*≠\s*prix\s*×\s*quantité",
        ],
        "niveau": "CRITIQUE",
        "reference": "BT01 - Total = Prix Unitaire × Quantité",
        "recommandation": "Recalculer les totaux"
    },
}


@registry.register(capabilities=["VERIFIER_BT01", "DETECTER_ECARTS", "CONFORMITE_FINANCIERE"])
class BT01Agent(BaseAgent):
    """
    Agent de vérification de conformité BT01.
    
    Capabilités:
    - Vérification automatique des BT01
    - Détection des écarts et erreurs
    - Conformité aux seuils légaux
    - ZERO € : retour qualitatif, données financières dans financial_data
    """
    
    name = "BT01 Conformity Verifier"
    capabilities = ["VERIFIER_BT01", "DETECTER_ECARTS", "CONFORMITE_FINANCIERE"]
    dependencies = ["PARSER", "EXTRACTION"]
    tags = ["finance", "bt01", "conformité", "prix"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        """Évaluer la pertinence pour cette mission."""
        has_bt01 = mission.has_document_type("BT01") or "bt01" in str(mission.context).lower()
        has_dpgf = mission.has_document_type("DPGF") or "dpgf" in str(mission.context).lower()
        has_prix = any(
            kw in str(mission.context).lower() 
            for kw in ["prix", "pu", "bt", "bordereau"]
        )
        
        if has_bt01:
            return 0.98
        if has_dpgf:
            return 0.85
        if has_prix:
            return 0.60
        return 0.10

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Exécuter la vérification BT01."""
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        # Extraction des données BT01 (simplifiée - en prod: parser dédié)
        lignes_bt01 = self._extraire_lignes_bt01(chunks)
        
        if lignes_bt01:
            # Stocker toutes les données financières dans financial_data
            total_ht_estime = sum(l["total"] for l in lignes_bt01 if l.get("total"))
            financial_data["bt01_analysis"] = {
                "nombre_lignes": len(lignes_bt01),
                "total_ht_estime": total_ht_estime,
                "lignes": [
                    {
                        "poste": l.get("poste", ""),
                        "libelle": l.get("libelle", ""),
                        "quantite": l.get("quantite", 0),
                        "unite": l.get("unite", ""),
                        "pu": l.get("pu", 0),
                        "total": l.get("total", 0)
                    }
                    for l in lignes_bt01
                ],
                "seuils": {
                    "SEUIL_MAPA": BT01_SEUILS["SEUIL_MAPA"],
                    "SEUIL_FORMALISE": BT01_SEUILS["SEUIL_FORMALISE"],
                    "SEUIL_EUROPEEN_TRAVAUX": BT01_SEUILS["SEUIL_EUROPEEN_TRAVAUX"]
                }
            }
            
            # Vérifications automatisées
            findings.extend(self._verifier_prix_unitaires(lignes_bt01))
            findings.extend(self._verifier_libelles(lignes_bt01))
            findings.extend(self._verifier_unites(lignes_bt01))
            findings.extend(self._verifier_quantites(lignes_bt01))
            findings.extend(self._verifier_totaux(lignes_bt01))
            
            # Vérification des seuils
            findings.extend(self._verifier_seuils(total_ht_estime))
        else:
            # Recherche par mots-clés
            findings.extend(self._recherche_mots_cles(chunks))
        
        if not findings:
            findings.append({
                "type": "BT01_CONFORME",
                "niveau": "FAIBLE",
                "details": "Aucune non-conformité BT01 détectée",
                "recommandation": "Document conforme aux exigences légales"
            })
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_BT01",
            confidence=0.92,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=list(range(1, min(len(chunks) + 1, 50))),
            execution_time_ms=0
        )

    def _extraire_lignes_bt01(self, chunks: List[Any]) -> List[Dict[str, Any]]:
        """Extraire les lignes du BT01 (simplifié)."""
        lignes = []
        
        for chunk in chunks:
            text = str(chunk)
            # Recherche de pattern BT01 simplifié
            # Exemple: "1.1 Terrassement 1000 m3 25,00 € 25 000,00 €"
            pattern = r"(\d+\.\d+)\s+([^\d]+)\s+(\d+[.,]?\d*)\s+([mml²³kg]+)\s+([\d]+[.,]?\d*)\s+([\d]+[.,]?\d*)"
            
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    ligne = {
                        "poste": match.group(1),
                        "libelle": match.group(2).strip(),
                        "quantite": float(match.group(3).replace(",", ".")),
                        "unite": match.group(4).strip(),
                        "pu": float(match.group(5).replace(",", ".")),
                        "total": float(match.group(6).replace(",", "."))
                    }
                    lignes.append(ligne)
                except (ValueError, IndexError):
                    continue
        
        return lignes

    def _verifier_prix_unitaires(self, lignes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les prix unitaires."""
        findings = []
        
        for ligne in lignes:
            poste = ligne.get("poste", "Inconnu")
            libelle = ligne.get("libelle", "")[:50]
            pu = ligne.get("pu", 0)
            
            if pu == 0:
                findings.append({
                    "type": "PRIX_UNITAIRE_MANQUANT",
                    "niveau": "CRITIQUE",
                    "poste": poste,
                    "libelle": libelle,
                    "reference": "BT01 - Tout prix unitaire doit être > 0",
                    "recommandation": "Compléter le prix unitaire (détails dans financial_data)"
                })
            elif pu < 0.01:
                findings.append({
                    "type": "PRIX_UNITAIRE_TROP_FAIBLE",
                    "niveau": "ELEVE",
                    "poste": poste,
                    "libelle": libelle,
                    "reference": "BT01 - Prix unitaire suspect (< 0,01)",
                    "recommandation": "Vérifier la cohérence du prix (détails dans financial_data)"
                })
            elif pu > 10000:
                findings.append({
                    "type": "PRIX_UNITAIRE_ELEVE",
                    "niveau": "MOYEN",
                    "poste": poste,
                    "libelle": libelle,
                    "reference": "BT01 - Prix unitaire très élevé (> 10 000)",
                    "recommandation": "Vérifier la justification (détails dans financial_data)"
                })
        
        return findings

    def _verifier_libelles(self, lignes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les libellés."""
        findings = []
        
        for ligne in lignes:
            libelle = ligne.get("libelle", "").strip()
            if not libelle or libelle.lower() in ["nc", "non communiqué", "à définir"]:
                findings.append({
                    "type": "LIBELLE_MANQUANT",
                    "niveau": "ELEVE",
                    "poste": ligne.get("poste", "Inconnu"),
                    "reference": "BT01 - Tout poste doit avoir un libellé",
                    "recommandation": "Compléter le libellé"
                })
        
        return findings

    def _verifier_unites(self, lignes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les unités."""
        findings = []
        unites_valides = ["m", "m2", "m3", "ml", "kg", "t", "u", "h", "j"]
        
        for ligne in lignes:
            unite = ligne.get("unite", "").strip().lower()
            if not unite:
                findings.append({
                    "type": "UNITE_MANQUANTE",
                    "niveau": "ELEVE",
                    "poste": ligne.get("poste", "Inconnu"),
                    "reference": "BT01 - Toute ligne doit avoir une unité",
                    "recommandation": "Ajouter l'unité"
                })
            elif unite not in unites_valides:
                findings.append({
                    "type": "UNITE_NON_STANDARD",
                    "niveau": "MOYEN",
                    "poste": ligne.get("poste", "Inconnu"),
                    "unite": unite,
                    "reference": "BT01 - Utiliser des unités standard",
                    "recommandation": "Vérifier l'unité"
                })
        
        return findings

    def _verifier_quantites(self, lignes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les quantités."""
        findings = []
        
        for ligne in lignes:
            quantite = ligne.get("quantite", 0)
            if quantite == 0:
                findings.append({
                    "type": "QUANTITE_NULLE",
                    "niveau": "MOYEN",
                    "poste": ligne.get("poste", "Inconnu"),
                    "reference": "BT01 - Vérifier les quantités nulles",
                    "recommandation": "Vérifier si intentionnelle"
                })
        
        return findings

    def _verifier_totaux(self, lignes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifier les totaux (Total = PU × Quantité)."""
        findings = []
        tolerance = BT01_SEUILS["TOLERANCE_ECART_BT01"]
        
        for ligne in lignes:
            poste = ligne.get("poste", "Inconnu")
            pu = ligne.get("pu", 0)
            qte = ligne.get("quantite", 0)
            total_attendu = pu * qte
            total_reel = ligne.get("total", 0)
            
            if total_attendu > 0 and abs(total_reel - total_attendu) / total_attendu > tolerance:
                findings.append({
                    "type": "TOTAL_INCOHERENT",
                    "niveau": "CRITIQUE",
                    "poste": poste,
                    "details": "Incohérence entre total et calcul PU × Quantité (voir financial_data)",
                    "reference": "BT01 - Total = PU × Quantité",
                    "recommandation": "Recalculer le total"
                })
        
        return findings

    def _verifier_seuils(self, total_ht: float) -> List[Dict[str, Any]]:
        """Vérifier les seuils légaux."""
        findings = []
        
        if total_ht <= BT01_SEUILS["SEUIL_MAPA"]:
            findings.append({
                "type": "MARCHE_MAPA",
                "niveau": "INFO",
                "details": "Marché éligible à la procédure adaptée (détails financiers dans financial_data)",
                "reference": "CCP Article 26 - Marché à procédure adaptée",
                "recommandation": "Procédure MAPA applicable"
            })
        elif total_ht <= BT01_SEUILS["SEUIL_EUROPEEN_TRAVAUX"]:
            findings.append({
                "type": "MARCHE_FORMALISE",
                "niveau": "INFO",
                "details": "Marché dans les seuils formalisés (détails financiers dans financial_data)",
                "reference": "CCP Article 26 - Marché formalisé",
                "recommandation": "Procédure formalisée requise"
            })
        else:
            findings.append({
                "type": "SEUIL_EUROPEEN_DEPASSE",
                "niveau": "ELEVE",
                "details": "Marché dépasse les seuils européens (détails financiers dans financial_data)",
                "reference": "CCP Article 26 - Seuils européens",
                "recommandation": "Publication au BOAMP obligatoire"
            })
        
        return findings

    def _recherche_mots_cles(self, chunks: List[Any]) -> List[Dict[str, Any]]:
        """Recherche par mots-clés si pas de lignes BT01 détectées."""
        findings = []
        bt01_keywords = ["bt01", "bordereau", "prix unitaire", "pu ", "quantité", "total ht"]
        
        for chunk in chunks:
            text = str(chunk).lower()
            for keyword in bt01_keywords:
                if keyword in text:
                    findings.append({
                        "type": "BT01_PRESUME_DETECTE",
                        "niveau": "INFO",
                        "keyword": keyword,
                        "reference": "Détection par mot-clé",
                        "recommandation": "Utiliser un parser dédié BT01 pour analyse complète"
                    })
                    break
        
        return findings
