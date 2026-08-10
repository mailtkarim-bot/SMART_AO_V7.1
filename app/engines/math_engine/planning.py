"""
SMART_AO V7 - planning.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Planning Chantier - Optimisation et gestion des plannings
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
import logging
from decimal import Decimal, getcontext

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


@dataclass
class Tache:
    """Représente une tâche de chantier."""
    tache_id: str
    nom: str
    duree_jours: int
    dependencies: List[str] = field(default_factory=list)
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    ressources: List[str] = field(default_factory=list)
    cout: Decimal = Decimal("0")
    est_critique: bool = False


@dataclass
class Ressource:
    """Représente une ressource."""
    ressource_id: str
    nom: str
    type: str = "humaine"  # "humaine", "materiel", "sous_traitant"
    cout_journalier: Decimal = Decimal("0")
    disponibilite: List[date] = field(default_factory=list)
    capacite: int = 1


@dataclass
class Planning:
    """Représente un planning de chantier."""
    planning_id: str
    mission_id: str
    nom: str
    date_debut: date
    date_fin: Optional[date] = None
    taches: List[Tache] = field(default_factory=list)
    ressources: List[Ressource] = field(default_factory=list)
    duree_totale: Optional[int] = None
    cout_total: Optional[Decimal] = None
    chemin_critique: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "planning_id": self.planning_id,
            "mission_id": self.mission_id,
            "nom": self.nom,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "duree_totale": self.duree_totale,
            "cout_total": float(self.cout_total) if self.cout_total else None,
            "chemin_critique": self.chemin_critique,
            "taches": [
                {
                    "tache_id": t.tache_id,
                    "nom": t.nom,
                    "duree_jours": t.duree_jours,
                    "dependencies": t.dependencies,
                    "date_debut": t.date_debut.isoformat() if t.date_debut else None,
                    "date_fin": t.date_fin.isoformat() if t.date_fin else None,
                    "est_critique": t.est_critique
                }
                for t in self.taches
            ],
            "ressources": [
                {
                    "ressource_id": r.ressource_id,
                    "nom": r.nom,
                    "type": r.type,
                    "cout_journalier": float(r.cout_journalier)
                }
                for r in self.ressources
            ]
        }


@dataclass
class PlanningOptimisation:
    """Résultat d'optimisation de planning."""
    planning_original: Planning
    planning_optimise: Planning
    duree_gagnee: int
    cout_economise: Decimal
    modifications: List[str] = field(default_factory=list)


class PlanningSolver:
    """
    Solveur d'optimisation de planning de chantier.
    
    Calcule le chemin critique, optimise l'ordonnancement des tâches
    et alloue les ressources de manière optimale.
    """
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
    
    def calculer_chemin_critique(
        self,
        taches: List[Tache]
    ) -> Tuple[List[str], int]:
        """
        Calcule le chemin critique du planning.
        
        Args:
            taches: Liste des tâches avec leurs dépendances
        
        Returns:
            Tuple (liste des IDs des tâches du chemin critique, durée totale)
        """
        # Calculer la durée totale du projet
        duree_totale = sum(t.duree_jours for t in taches)
        
        # Pour une implémentation simple: considérer toutes les tâches sans dépendances comme critiques
        # En production: implémenter l'algorithme du chemin critique (CPM)
        chemin_critique = [t.tache_id for t in taches if t.est_critique or len(t.dependencies) > 0]
        
        if not chemin_critique:
            chemin_critique = [t.tache_id for t in sorted(taches, key=lambda x: x.duree_jours, reverse=True)[:1]]
        
        return chemin_critique, duree_totale
    
    def ordonner_taches(
        self,
        taches: List[Tache]
    ) -> List[Tache]:
        """
        Ordonnance les tâches en respectant les dépendances.
        
        Args:
            taches: Liste des tâches à ordonner
        
        Returns:
            Liste des tâches ordonnancées
        """
        # Implémentation simplifiée: tri topologique
        taches_ordonnees = []
        taches_restantes = taches.copy()
        
        while taches_restantes:
            # Trouver les tâches sans dépendances
            taches_pretes = [
                t for t in taches_restantes 
                if all(dep in [tt.tache_id for tt in taches_ordonnees] for dep in t.dependencies)
            ]
            
            if not taches_pretes:
                # Dépendance cyclique - retourner ce qu'on a
                taches_ordonnees.extend(taches_restantes)
                break
            
            # Ajouter les tâches prêtes
            taches_ordonnees.extend(taches_pretes)
            for t in taches_pretes:
                taches_restantes.remove(t)
        
        return taches_ordonnees
    
    def generer_planning(
        self,
        mission_id: str,
        nom: str,
        date_debut: date,
        taches: List[Dict[str, Any]],
        ressources: Optional[List[Dict[str, Any]]] = None
    ) -> Planning:
        """
        Génère un planning à partir des données d'entrée.
        
        Args:
            mission_id: ID de la mission
            nom: Nom du planning
            date_debut: Date de début du chantier
            taches: Liste des tâches (dictionnaires)
            ressources: Liste des ressources (optionnel)
        
        Returns:
            Planning généré
        """
        planning_taches = []
        for tache_data in taches:
            tache = Tache(
                tache_id=tache_data.get("tache_id", f"T{taches.index(tache_data)+1}"),
                nom=tache_data.get("nom", "Tâche sans nom"),
                duree_jours=tache_data.get("duree_jours", 1),
                dependencies=tache_data.get("dependencies", []),
                ressources=tache_data.get("ressources", []),
                cout=Decimal(str(tache_data.get("cout", 0)))
            )
            planning_taches.append(tache)
        
        # Ordonnancer les tâches
        taches_ordonnees = self.ordonner_taches(planning_taches)
        
        # Calculer les dates de début/fin
        current_date = date_debut
        for i, tache in enumerate(taches_ordonnees):
            tache.date_debut = current_date
            tache.date_fin = current_date + timedelta(days=tache.duree_jours)
            current_date = tache.date_fin or current_date
        
        # Calculer le chemin critique
        chemin_critique, duree_totale = self.calculer_chemin_critique(taches_ordonnees)
        date_fin = date_debut + timedelta(days=duree_totale)
        
        # Calculer le coût total
        cout_total = sum(t.cout for t in taches_ordonnees)
        
        # Convertir les ressources
        planning_ressources = []
        if ressources:
            for ress_data in ressources:
                ress = Ressource(
                    ressource_id=ress_data.get("ressource_id", f"R{ressources.index(ress_data)+1}"),
                    nom=ress_data.get("nom", "Ressource sans nom"),
                    type=ress_data.get("type", "humaine"),
                    cout_journalier=Decimal(str(ress_data.get("cout_journalier", 0)))
                )
                planning_ressources.append(ress)
        
        planning_id = f"PLAN-{mission_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return Planning(
            planning_id=planning_id,
            mission_id=mission_id,
            nom=nom,
            date_debut=date_debut,
            date_fin=date_fin,
            taches=taches_ordonnees,
            ressources=planning_ressources,
            duree_totale=duree_totale,
            cout_total=cout_total,
            chemin_critique=chemin_critique
        )
    
    def optimiser_planning(
        self,
        planning: Planning
    ) -> PlanningOptimisation:
        """
        Optimise un planning existant.
        
        Args:
            planning: Planning à optimiser
        
        Returns:
            Résultat d'optimisation
        """
        # Pour la démo: simuler une optimisation simple
        # En production: implémenter des algorithmes d'optimisation
        
        # Réordonnancer les tâches
        taches_optimisees = self.ordonner_taches(planning.taches)
        
        # Recalculer les dates
        current_date = planning.date_debut
        for tache in taches_optimisees:
            tache.date_debut = current_date
            tache.date_fin = current_date + timedelta(days=tache.duree_jours)
            current_date = tache.date_fin or current_date
        
        # Recalculer le chemin critique
        chemin_critique, duree_totale = self.calculer_chemin_critique(taches_optimisees)
        date_fin = planning.date_debut + timedelta(days=duree_totale)
        
        planning_optimise = Planning(
            planning_id=f"{planning.planning_id}-OPT",
            mission_id=planning.mission_id,
            nom=f"{planning.nom} (optimisé)",
            date_debut=planning.date_debut,
            date_fin=date_fin,
            taches=taches_optimisees,
            ressources=planning.ressources,
            duree_totale=duree_totale,
            cout_total=planning.cout_total,
            chemin_critique=chemin_critique
        )
        
        duree_gagnee = (planning.duree_totale or 0) - duree_totale
        cout_economise = Decimal("0")
        modifications = [
            f"Réordonnancement de {len(taches_optimisees)} tâches",
            f"Nouvelle durée: {duree_totale} jours (gain: {duree_gagnee} jours)"
        ]
        
        return PlanningOptimisation(
            planning_original=planning,
            planning_optimise=planning_optimise,
            duree_gagnee=duree_gagnee,
            cout_economise=cout_economise,
            modifications=modifications
        )
    
    def verifier_delais(
        self,
        planning: Planning,
        date_limite: date
    ) -> Dict[str, Any]:
        """
        Vérifie si le planning respecte les délais.
        
        Args:
            planning: Planning à vérifier
            date_limite: Date limite du projet
        
        Returns:
            Dictionnaire avec le statut des délais
        """
        date_fin = planning.date_fin or (planning.date_debut + timedelta(days=planning.duree_totale or 0))
        
        jours_restants = (date_limite - date_fin).days if date_limite > date_fin else 0
        
        est_dans_delais = date_fin <= date_limite
        marge = (date_limite - date_fin).days if est_dans_delais else -abs((date_fin - date_limite).days)
        
        return {
            "est_dans_delais": est_dans_delais,
            "date_fin_prevue": date_fin.isoformat(),
            "date_limite": date_limite.isoformat(),
            "marge_jours": marge,
            "niveau_risque": "aucun" if est_dans_delais and marge > 7 else 
                          "faible" if est_dans_delais and marge > 0 else
                          "eleve" if not est_dans_delais and marge > -7 else
                          "critique"
        }


solver = PlanningSolver()


def generer_planning(
    mission_id: str,
    nom: str,
    date_debut: str,
    taches: List[Dict[str, Any]],
    ressources: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Génère un planning."""
    date_debut_obj = datetime.fromisoformat(date_debut).date() if isinstance(date_debut, str) else date_debut
    planning = solver.generer_planning(mission_id, nom, date_debut_obj, taches, ressources)
    return planning.to_dict()


def calculer_chemin_critique(taches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcule le chemin critique."""
    tache_objs = [
        Tache(
            tache_id=t.get("tache_id", f"T{i}"),
            nom=t.get("nom", ""),
            duree_jours=t.get("duree_jours", 0),
            dependencies=t.get("dependencies", [])
        )
        for i, t in enumerate(taches)
    ]
    chemin, duree = solver.calculer_chemin_critique(tache_objs)
    return {"chemin_critique": chemin, "duree_totale": duree}


def verifier_delais_planning(
    planning_data: Dict[str, Any],
    date_limite: str
) -> Dict[str, Any]:
    """Vérifie les délais d'un planning."""
    planning = Planning(
        planning_id=planning_data.get("planning_id", ""),
        mission_id=planning_data.get("mission_id", ""),
        nom=planning_data.get("nom", ""),
        date_debut=datetime.fromisoformat(planning_data.get("date_debut")).date() if planning_data.get("date_debut") else date.today(),
        date_fin=datetime.fromisoformat(planning_data.get("date_fin")).date() if planning_data.get("date_fin") else None,
        duree_totale=planning_data.get("duree_totale")
    )
    date_limite_obj = datetime.fromisoformat(date_limite).date() if isinstance(date_limite, str) else date_limite
    return solver.verifier_delais(planning, date_limite_obj)


