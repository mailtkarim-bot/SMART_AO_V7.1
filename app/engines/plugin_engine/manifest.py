"""
SMART_AO V7 - manifest.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Plugin Manifest - Gestion des manifestes de plugins
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PluginDependency:
    """Représente une dépendance de plugin."""
    nom: str
    version_min: Optional[str] = None
    version_max: Optional[str] = None
    obligatoire: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "nom": self.nom,
            "version_min": self.version_min,
            "version_max": self.version_max,
            "obligatoire": self.obligatoire
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginDependency":
        """Créer à partir d'un dictionnaire."""
        return cls(
            nom=data.get("nom", data.get("name", "")),
            version_min=data.get("version_min", data.get("min_version")),
            version_max=data.get("version_max", data.get("max_version")),
            obligatoire=data.get("obligatoire", data.get("required", True))
        )


@dataclass
class PluginMetadata:
    """Métadonnées d'un plugin."""
    nom: str
    version: str
    description: str
    auteur: str
    licence: str = "Proprietary"
    site_web: Optional[str] = None
    email: Optional[str] = None
    date_creation: str = datetime.utcnow().strftime("%Y-%m-%d")
    date_mise_a_jour: str = datetime.utcnow().strftime("%Y-%m-%d")
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    dependances: List[PluginDependency] = field(default_factory=list)
    compatibilite: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "nom": self.nom,
            "version": self.version,
            "description": self.description,
            "auteur": self.auteur,
            "licence": self.licence,
            "site_web": self.site_web,
            "email": self.email,
            "date_creation": self.date_creation,
            "date_mise_a_jour": self.date_mise_a_jour,
            "tags": self.tags,
            "categories": self.categories,
            "dependances": [d.to_dict() for d in self.dependances],
            "compatibilite": self.compatibilite
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Créer à partir d'un dictionnaire."""
        return cls(
            nom=data.get("nom", data.get("name", "")),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            auteur=data.get("auteur", data.get("author", "")),
            licence=data.get("licence", data.get("license", "Proprietary")),
            site_web=data.get("site_web", data.get("website")),
            email=data.get("email"),
            date_creation=data.get("date_creation", data.get("created_at", datetime.utcnow().strftime("%Y-%m-%d"))),
            date_mise_a_jour=data.get("date_mise_a_jour", data.get("updated_at", datetime.utcnow().strftime("%Y-%m-%d"))),
            tags=data.get("tags", []),
            categories=data.get("categories", []),
            dependances=[PluginDependency.from_dict(d) for d in data.get("dependances", data.get("dependencies", []))],
            compatibilite=data.get("compatibilite", data.get("compatibility", []))
        )


@dataclass
class PluginManifest:
    """Manifeste complet d'un plugin."""
    manifest_id: str
    plugin_id: str
    metadata: PluginMetadata
    entry_point: str
    fichiers: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    routes: List[Dict[str, Any]] = field(default_factory=list)
    hooks: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "manifest_id": self.manifest_id,
            "plugin_id": self.plugin_id,
            "metadata": self.metadata.to_dict(),
            "entry_point": self.entry_point,
            "fichiers": self.fichiers,
            "configuration": self.configuration,
            "permissions": self.permissions,
            "routes": self.routes,
            "hooks": self.hooks
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convertir en JSON."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        """Créer à partir d'un dictionnaire."""
        metadata = PluginMetadata.from_dict(data.get("metadata", {}))
        return cls(
            manifest_id=data.get("manifest_id", ""),
            plugin_id=data.get("plugin_id", ""),
            metadata=metadata,
            entry_point=data.get("entry_point", data.get("entry", "")),
            fichiers=data.get("fichiers", data.get("files", [])),
            configuration=data.get("configuration", data.get("config", {})),
            permissions=data.get("permissions", []),
            routes=data.get("routes", []),
            hooks=data.get("hooks", [])
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> "PluginManifest":
        """Charger depuis un fichier JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """Sauvegarder dans un fichier JSON."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        logger.info(f"Manifest sauvegarde: {file_path}")


@dataclass
class PluginRegistration:
    """Enregistrement d'un plugin dans le système."""
    plugin_id: str
    manifest: PluginManifest
    date_enregistrement: datetime = field(default_factory=datetime.utcnow)
    statu: str = "active"
    chemin: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "plugin_id": self.plugin_id,
            "manifest": self.manifest.to_dict(),
            "date_enregistrement": self.date_enregistrement.isoformat(),
            "statu": self.statu,
            "chemin": self.chemin
        }


class PluginManifestManager:
    """
    Gestionnaire des manifestes de plugins.
    
    Charge, valide et gère les manifestes des plugins SMART_AO V7.
    """
    
    SCHEMA_VERSION = "1.0"
    SUPPORTED_VERSIONS = ["1.0"]
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.manifests: Dict[str, PluginManifest] = {}
        self.registrations: Dict[str, PluginRegistration] = {}
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """Charge les plugins depuis le répertoire."""
        if not self.plugins_dir.exists():
            logger.warning(f"Repertoire plugins introuvable: {self.plugins_dir}")
            return
        
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = PluginManifest.from_file(str(manifest_path))
                        self.manifests[manifest.plugin_id] = manifest
                        
                        registration = PluginRegistration(
                            plugin_id=manifest.plugin_id,
                            manifest=manifest,
                            chemin=str(plugin_dir)
                        )
                        self.registrations[manifest.plugin_id] = registration
                        logger.info(f"Plugin charge: {manifest.plugin_id} v{manifest.metadata.version}")
                    except Exception as e:
                        logger.error(f"Erreur de chargement du manifest {manifest_path}: {e}")
    
    def get_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Récupère un manifeste par ID de plugin."""
        return self.manifests.get(plugin_id)
    
    def get_registration(self, plugin_id: str) -> Optional[PluginRegistration]:
        """Récupère l'enregistrement d'un plugin."""
        return self.registrations.get(plugin_id)
    
    def register_plugin(
        self,
        plugin_id: str,
        manifest: PluginManifest,
        chemin: str
    ) -> PluginRegistration:
        """Enregistre un plugin."""
        registration = PluginRegistration(
            plugin_id=plugin_id,
            manifest=manifest,
            chemin=chemin
        )
        self.manifests[plugin_id] = manifest
        self.registrations[plugin_id] = registration
        logger.info(f"Plugin enregistre: {plugin_id}")
        return registration
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Désenregistre un plugin."""
        if plugin_id in self.registrations:
            del self.registrations[plugin_id]
            del self.manifests[plugin_id]
            logger.info(f"Plugin desenregistre: {plugin_id}")
            return True
        return False
    
    def get_all_manifests(self) -> Dict[str, PluginManifest]:
        """Récupère tous les manifestes."""
        return self.manifests.copy()
    
    def get_plugins_by_category(self, category: str) -> List[PluginManifest]:
        """Récupère les plugins par catégorie."""
        return [
            m for m in self.manifests.values()
            if category in m.metadata.categories
        ]
    
    def get_plugins_by_tag(self, tag: str) -> List[PluginManifest]:
        """Récupère les plugins par tag."""
        return [
            m for m in self.manifests.values()
            if tag in m.metadata.tags
        ]
    
    def get_plugins_by_author(self, author: str) -> List[PluginManifest]:
        """Récupère les plugins par auteur."""
        return [
            m for m in self.manifests.values()
            if m.metadata.auteur == author
        ]
    
    def validate_manifest(self, manifest: PluginManifest) -> Tuple[bool, List[str]]:
        """
        Valide un manifeste de plugin.
        
        Returns:
            Tuple (est_valide, liste_erreurs)
        """
        erreurs = []
        
        # Vérifier les champs obligatoires
        if not manifest.plugin_id:
            erreurs.append("plugin_id est obligatoire")
        
        if not manifest.entry_point:
            erreurs.append("entry_point est obligatoire")
        
        # Vérifier les métadonnées
        if not manifest.metadata.nom:
            erreurs.append("metadata.nom est obligatoire")
        
        if not manifest.metadata.version:
            erreurs.append("metadata.version est obligatoire")
        
        if not manifest.metadata.auteur:
            erreurs.append("metadata.auteur est obligatoire")
        
        # Vérifier la version
        try:
            from packaging import version
            version.parse(manifest.metadata.version)
        except (ImportError, Exception):
            erreurs.append("metadata.version n'est pas une version valide (format: X.Y.Z)")
        
        return len(erreurs) == 0, erreurs
    
    def check_dependencies(
        self,
        manifest: PluginManifest,
        installed_plugins: Set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Vérifie les dépendances d'un plugin.
        
        Args:
            manifest: Manifeste du plugin
            installed_plugins: Ensemble des plugins installés
            
        Returns:
            Tuple (toutes_deps_satisfaites, liste_erreurs)
        """
        erreurs = []
        
        for dep in manifest.metadata.dependances:
            if dep.obligatoire and dep.nom not in installed_plugins:
                erreurs.append(f"Dependance manquante: {dep.nom}")
        
        return len(erreurs) == 0, erreurs
    
    def check_compatibility(self, manifest: PluginManifest) -> Tuple[bool, List[str]]:
        """
        Vérifie la compatibilité d'un plugin.
        
        Returns:
            Tuple (est_compatible, liste_erreurs)
        """
        erreurs = []
        
        # Vérifier la version du schéma
        if self.SCHEMA_VERSION not in manifest.metadata.compatibilite:
            erreurs.append(f"Schema version {self.SCHEMA_VERSION} non supporte")
        
        return len(erreurs) == 0, erreurs
    
    def create_manifest(
        self,
        plugin_id: str,
        nom: str,
        version: str,
        description: str,
        auteur: str,
        entry_point: str,
        **kwargs
    ) -> PluginManifest:
        """Crée un manifeste de plugin."""
        metadata = PluginMetadata(
            nom=nom,
            version=version,
            description=description,
            auteur=auteur,
            **{k: v for k, v in kwargs.items() if k not in ['fichiers', 'configuration', 'permissions', 'routes', 'hooks']}
        )
        
        manifest = PluginManifest(
            manifest_id=f"MANIFEST_{plugin_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            plugin_id=plugin_id,
            metadata=metadata,
            entry_point=entry_point,
            **{k: v for k, v in kwargs.items() if k in ['fichiers', 'configuration', 'permissions', 'routes', 'hooks']}
        )
        
        return manifest


manager = PluginManifestManager()


def create_manifest(
    plugin_id: str,
    nom: str,
    version: str,
    description: str,
    auteur: str,
    entry_point: str,
    fichiers: Optional[List[str]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    permissions: Optional[List[str]] = None,
    routes: Optional[List[Dict[str, Any]]] = None,
    hooks: Optional[List[Dict[str, Any]]] = None,
    licence: str = "Proprietary",
    tags: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    dependances: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Cree un manifeste de plugin."""
    manifest = manager.create_manifest(
        plugin_id=plugin_id,
        nom=nom,
        version=version,
        description=description,
        auteur=auteur,
        entry_point=entry_point,
        fichiers=fichiers or [],
        configuration=configuration or {},
        permissions=permissions or [],
        routes=routes or [],
        hooks=hooks or [],
        licence=licence,
        tags=tags or [],
        categories=categories or [],
        dependances=[PluginDependency.from_dict(d) for d in (dependances or [])]
    )
    return manifest.to_dict()


def get_manifest(plugin_id: str) -> Optional[Dict[str, Any]]:
    """Recupere un manifeste de plugin."""
    manifest = manager.get_manifest(plugin_id)
    return manifest.to_dict() if manifest else None


def get_all_manifests() -> Dict[str, Dict[str, Any]]:
    """Recupere tous les manifestes."""
    return {pid: m.to_dict() for pid, m in manager.get_all_manifests().items()}


def validate_manifest(manifest_data: Dict[str, Any]) -> Dict[str, Any]:
    """Valide un manifeste."""
    manifest = PluginManifest.from_dict(manifest_data)
    is_valid, errors = manager.validate_manifest(manifest)
    return {"valide": is_valid, "erreurs": errors}


def check_dependencies(plugin_id: str, installed_plugins: List[str]) -> Dict[str, Any]:
    """Verifie les dependances d'un plugin."""
    manifest = manager.get_manifest(plugin_id)
    if not manifest:
        return {"valide": False, "erreurs": [f"Plugin {plugin_id} non trouve"]}
    
    is_valid, errors = manager.check_dependencies(manifest, set(installed_plugins))
    return {"valide": is_valid, "erreurs": errors}


