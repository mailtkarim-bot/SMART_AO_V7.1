"""
SMART_AO V7 - Filesystem MCP Tools
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Filesystem MCP - Outils MCP pour la gestion du système de fichiers dans SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §4.5
"""

import logging
import os
import shutil
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="SMART_AO_Filesystem_MCP",
    version="7.1.0",
    description="Outils MCP pour la gestion avancée du système de fichiers"
)


@mcp.tool()
async def list_directory(
    path: str,
    recursive: bool = False,
    include_hidden: bool = False,
    pattern: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lister le contenu d'un répertoire."""
    logger.info(f"Liste du répertoire: {path}")
    
    if not os.path.exists(path):
        return [{"error": "Chemin non trouvé", "path": path}]
    
    try:
        items = []
        for item in os.listdir(path):
            if not include_hidden and item.startswith('.'):
                continue
            if pattern and pattern not in item:
                continue
                
            full_path = os.path.join(path, item)
            stat = os.stat(full_path)
            
            items.append({
                "name": item,
                "path": full_path,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        if recursive:
            for item in items:
                if item["type"] == "directory":
                    sub_items = await list_directory(
                        item["path"], 
                        recursive=True, 
                        include_hidden=include_hidden,
                        pattern=pattern
                    )
                    item["children"] = sub_items
        
        return items
    except Exception as e:
        logger.error(f"Erreur liste répertoire: {e}")
        return [{"error": str(e)}]


@mcp.tool()
async def read_file(
    file_path: str,
    encoding: str = "utf-8",
    max_size: int = 1048576  # 1MB
) -> Dict[str, Any]:
    """Lire le contenu d'un fichier."""
    logger.info(f"Lecture du fichier: {file_path}")
    
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé", "path": file_path}
    
    if os.path.isdir(file_path):
        return {"error": "Le chemin est un répertoire", "path": file_path}
    
    try:
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return {"error": f"Fichier trop grand ({file_size} > {max_size})"}
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return {
            "success": True,
            "path": file_path,
            "content": content,
            "size": file_size,
            "encoding": encoding
        }
    except Exception as e:
        logger.error(f"Erreur lecture fichier: {e}")
        return {"error": str(e)}


@mcp.tool()
async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    overwrite: bool = False
) -> Dict[str, Any]:
    """Écrire du contenu dans un fichier."""
    logger.info(f"Écriture du fichier: {file_path}")
    
    if os.path.exists(file_path) and not overwrite:
        return {"error": "Fichier existe déjà", "path": file_path, "suggestion": "overwrite=True"}
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "path": file_path,
            "bytes_written": len(content.encode(encoding)),
            "message": "Fichier écrit avec succès"
        }
    except Exception as e:
        logger.error(f"Erreur écriture fichier: {e}")
        return {"error": str(e)}


@mcp.tool()
async def copy_file(
    source: str,
    destination: str,
    overwrite: bool = False
) -> Dict[str, Any]:
    """Copier un fichier."""
    logger.info(f"Copie: {source} -> {destination}")
    
    if not os.path.exists(source):
        return {"error": "Source non trouvée", "path": source}
    
    if os.path.exists(destination) and not overwrite:
        return {"error": "Destination existe déjà", "suggestion": "overwrite=True"}
    
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(source, destination)
        
        return {
            "success": True,
            "source": source,
            "destination": destination,
            "message": "Fichier copié avec succès"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def delete_file(path: str) -> Dict[str, Any]:
    """Supprimer un fichier."""
    logger.info(f"Suppression: {path}")
    
    if not os.path.exists(path):
        return {"error": "Fichier non trouvé", "path": path}
    
    if os.path.isdir(path):
        return {"error": "Le chemin est un répertoire", "suggestion": "Utiliser delete_directory"}
    
    try:
        os.remove(path)
        return {"success": True, "path": path, "message": "Fichier supprimé"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def create_directory(path: str, parents: bool = True) -> Dict[str, Any]:
    """Créer un répertoire."""
    logger.info(f"Création répertoire: {path}")
    
    try:
        os.makedirs(path, exist_ok=parents)
        return {
            "success": True,
            "path": path,
            "exists": os.path.exists(path),
            "message": "Répertoire créé"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def file_hash(path: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """Calculer le hash d'un fichier."""
    logger.info(f"Hash du fichier: {path}")
    
    if not os.path.exists(path):
        return {"error": "Fichier non trouvé"}
    
    try:
        hash_func = getattr(hashlib, algorithm)()
        
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return {
            "path": path,
            "algorithm": algorithm,
            "hash": hash_func.hexdigest(),
            "size": os.path.getsize(path)
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_file_info(path: str) -> Dict[str, Any]:
    """Obtenir les informations d'un fichier."""
    logger.info(f"Infoms fichier: {path}")
    
    if not os.path.exists(path):
        return {"error": "Fichier non trouvé"}
    
    try:
        stat = os.stat(path)
        
        return {
            "path": path,
            "name": os.path.basename(path),
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:]
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    logger.info("Démarrage du serveur Filesystem MCP...")
    mcp.run()


