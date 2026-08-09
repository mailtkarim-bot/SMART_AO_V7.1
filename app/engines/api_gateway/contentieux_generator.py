"""
Contentieux Generator - Génération automatique de dossiers contentieux
Analyse l'historique des litiges et génère des rapports pour anticipation risques
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ContentieuxItem(BaseModel):
    """Un contentieux individuel"""
    id: str
    date_ouverture: datetime
    type_litige: str  # "retard_paiement", "malfacon", "penalites_retard", "resiliation"
    partie_adverse: str
    montant_enjeu: Decimal
    statut: str  # "en_cours", "resolu", "abandonne"
    decision: Optional[str] = None
    date_cloture: Optional[datetime] = None


class ContentieuxAnalysisResult(BaseModel):
    """Résultat d'analyse contentieux"""
    entreprise_siret: str
    total_contentieux: int
    contentieux_en_cours: int
    montant_total_enjeu: Decimal
    types_litiges_recurrents: List[str]
    risque_global: str  # "faible", "moyen", "eleve", "critique"
    recommandations: List[str]
    historique: List[ContentieuxItem] = Field(default_factory=list)


class ContentieuxGenerator:
    """Générateur de dossiers contentieux"""
    
    SEUILS_RISQUE = {
        "faible": {"max_encours": 50000, "max_nb": 2},
        "moyen": {"max_encours": 200000, "max_nb": 5},
        "eleve": {"max_encours": 500000, "max_nb": 10},
        "critique": {"max_encours": float("inf"), "max_nb": float("inf")}
    }
    
    def __init__(self):
        self.types_litiges_standards = [
            "retard_paiement", "malfacon", "penalites_retard",
            "resiliation", "garantie_decennale", "desordre_majeur"
        ]
    
    def generer_dossier_contentieux(
        self,
        siret: str,
        historique_brut: List[Dict[str, Any]]
    ) -> ContentieuxAnalysisResult:
        """Génère un dossier contentieux complet"""
        contentieux_items = []
        
        for item in historique_brut:
            contentieux = ContentieuxItem(
                id=item.get("id", f"CONT-{len(contentieux_items)+1}"),
                date_ouverture=datetime.fromisoformat(item["date_ouverture"]) if isinstance(item.get("date_ouverture"), str) else item.get("date_ouverture", datetime.now()),
                type_litige=item.get("type_litige", "inconnu"),
                partie_adverse=item.get("partie_adverse", "Non spécifié"),
                montant_enjeu=Decimal(str(item.get("montant_enjeu", 0))),
                statut=item.get("statut", "en_cours"),
                decision=item.get("decision"),
                date_cloture=datetime.fromisoformat(item["date_cloture"]) if item.get("date_cloture") and isinstance(item["date_cloture"], str) else item.get("date_cloture")
            )
            contentieux_items.append(contentieux)
        
        en_cours = [c for c in contentieux_items if c.statut == "en_cours"]
        montant_total = sum(c.montant_enjeu for c in en_cours)
        
        # Analyse types récurrents
        types_counts = {}
        for c in contentieux_items:
            types_counts[c.type_litige] = types_counts.get(c.type_litige, 0) + 1
        types_recurrents = sorted(types_counts.keys(), key=lambda x: types_counts[x], reverse=True)[:3]
        
        # Évaluation risque global
        risque = self._evaluer_risque_global(len(en_cours), montant_total)
        
        # Génération recommandations
        recommandations = self._generer_recommandations(contentieux_items, risque)
        
        return ContentieuxAnalysisResult(
            entreprise_siret=siret,
            total_contentieux=len(contentieux_items),
            contentieux_en_cours=len(en_cours),
            montant_total_enjeu=montant_total,
            types_litiges_recurrents=types_recurrents,
            risque_global=risque,
            recommandations=recommandations,
            historique=contentieux_items
        )
    
    def _evaluer_risque_global(self, nb_encours: int, montant: Decimal) -> str:
        """Évalue le niveau de risque global"""
        for niveau, seuils in sorted(self.SEUILS_RISQUE.items(), key=lambda x: x[1]["max_encours"]):
            if nb_encours <= seuils["max_nb"] and montant <= seuils["max_encours"]:
                return niveau
        return "critique"
    
    def _generer_recommandations(
        self,
        contentieux: List[ContentieuxItem],
        risque: str
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recos = []
        
        if risque == "critique":
            recos.append("🔴 RISQUE CRITIQUE : Suspension temporaire des soumissions recommandée")
            recos.append("Audit juridique complet requis avant nouveaux marchés")
        
        # Analyse par type de litige
        types_counts = {}
        for c in contentieux:
            types_counts[c.type_litige] = types_counts.get(c.type_litige, 0) + 1
        
        if types_counts.get("retard_paiement", 0) >= 3:
            recos.append("⚠️ Retards de paiement récurrents : Renforcer clauses de paiement dans contrats")
        
        if types_counts.get("malfacon", 0) >= 2:
            recos.append("⚠️ Malfaçons répétées : Mettre en place contrôle qualité renforcé")
        
        if types_counts.get("penalites_retard", 0) >= 2:
            recos.append("⚠️ Pénalités de retard fréquentes : Réviser planning et ressources")
        
        if not recos:
            recos.append("✅ Situation contentieuse maîtrisée")
        
        return recos
    
    def extraire_lecons_apprises(
        self,
        contentieux_resolus: List[ContentieuxItem]
    ) -> Dict[str, Any]:
        """Extrait les leçons apprises des contentieux résolus"""
        lecons = {
            "causes_frequentes": [],
            "cout_moyen_resolution": Decimal(0),
            "delai_moyen_resolution_jours": 0,
            "taux_succes": 0.0
        }
        
        resolus = [c for c in contentieux_resolus if c.statut == "resolu" and c.decision]
        
        if resolus:
            # Causes fréquentes
            causes = {}
            for c in resolus:
                causes[c.type_litige] = causes.get(c.type_litige, 0) + 1
            lecons["causes_frequentes"] = list(causes.keys())[:3]
            
            # Coût moyen
            total_montant = sum(c.montant_enjeu for c in resolus)
            lecons["cout_moyen_resolution"] = total_montant / len(resolus)
            
            # Délai moyen
            delais = []
            for c in resolus:
                if c.date_cloture and c.date_ouverture:
                    delai = (c.date_cloture - c.date_ouverture).days
                    delais.append(delai)
            if delais:
                lecons["delai_moyen_resolution_jours"] = sum(delais) / len(delais)
            
            # Taux de succès (décision favorable)
            succes = sum(1 for c in resolus if "favorable" in (c.decision or "").lower())
            lecons["taux_succes"] = succes / len(resolus) * 100
        
        return lecons


generator = ContentieuxGenerator()


def generer_analysis_contentieux(siret: str, historique: List[Dict[str, Any]]) -> ContentieuxAnalysisResult:
    """Fonction utilitaire"""
    return generator.generer_dossier_contentieux(siret, historique)
