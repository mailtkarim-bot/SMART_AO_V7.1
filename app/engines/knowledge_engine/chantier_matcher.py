"""Chantier Matcher - Correspondance entre offres et chantiers historiques"""
from typing import List, Dict, Any, Optional
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class ChantierMatcher:
    """Matche un nouvel AO avec les chantiers historiques similaires"""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcule le score de similarité entre deux textes"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def match_by_type(self, new_ao: Dict, historical_projects: List[Dict]) -> List[Dict]:
        """Match par type de travaux"""
        matches = []
        new_type = new_ao.get("type_travaux", "").lower()
        
        for project in historical_projects:
            proj_type = project.get("type_travaux", "").lower()
            similarity = self.calculate_similarity(new_type, proj_type)
            
            if similarity >= self.similarity_threshold:
                matches.append({
                    "project": project,
                    "similarity": similarity,
                    "match_type": "type_travaux"
                })
        
        return sorted(matches, key=lambda x: x["similarity"], reverse=True)
    
    def match_by_location(self, new_ao: Dict, historical_projects: List[Dict]) -> List[Dict]:
        """Match par zone géographique"""
        matches = []
        new_loc = new_ao.get("localisation", "").lower()
        
        for project in historical_projects:
            proj_loc = project.get("localisation", "").lower()
            
            # Match exact ou département proche
            if new_loc == proj_loc or self._same_department(new_loc, proj_loc):
                matches.append({
                    "project": project,
                    "similarity": 0.9,
                    "match_type": "location"
                })
        
        return matches
    
    def _same_department(self, loc1: str, loc2: str) -> bool:
        """Vérifie si deux localisations sont dans le même département"""
        # Extraction code département (simplifié)
        dep1 = loc1[:2] if len(loc1) >= 2 else ""
        dep2 = loc2[:2] if len(loc2) >= 2 else ""
        return dep1 == dep2 and dep1.isdigit()
    
    def find_similar_projects(
        self, 
        new_ao: Dict, 
        historical_projects: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """Trouve les projets historiques les plus similaires"""
        type_matches = self.match_by_type(new_ao, historical_projects)
        location_matches = self.match_by_location(new_ao, historical_projects)
        
        # Fusion et déduplication
        all_matches = {}
        for match in type_matches + location_matches:
            proj_id = match["project"].get("id")
            if proj_id not in all_matches:
                all_matches[proj_id] = match
            else:
                # Moyenne pondérée des scores
                all_matches[proj_id]["similarity"] = (
                    all_matches[proj_id]["similarity"] + match["similarity"]
                ) / 2
        
        return list(all_matches.values())[:limit]

# Instance globale
matcher = ChantierMatcher()
