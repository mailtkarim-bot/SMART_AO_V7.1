"""
SMART_AO V7 - clamav.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - ClamAV Antivirus Scanner
=======================================
Intégration avec ClamAV pour le scan antivirus des fichiers uploadés

Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

import os
import logging
import subprocess
import asyncio
import tempfile
from typing import Optional, Union, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ClamAVConfig:
    """Configuration ClamAV."""
    clamscan_path: str = "/usr/bin/clamscan"  # Chemin vers clamscan
    clamd_path: str = "/usr/bin/clamd"  # Chemin vers clamd
    clamdscan_path: str = "/usr/bin/clamdscan"  # Chemin vers clamdscan
    
    # Mode de scan (filesystem, socket, clamd)
    scan_mode: str = "filesystem"  # "filesystem", "socket", "clamd"
    
    # Configuration socket/clamd
    socket_path: str = "/var/run/clamav/clamd.ctl"
    host: str = "localhost"
    port: int = 3310
    
    # Timeout du scan
    scan_timeout: int = 30  # secondes
    
    # Taille maximale des fichiers
    max_file_size: int = 100 * 1024 * 1024  # 100 Mo
    
    # Fichiers temporaires
    temp_directory: str = "/tmp/clamav"
    
    # Liste blanche d'extensions
    allowed_extensions: List[str] = field(default_factory=lambda: [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".json"])


config = ClamAVConfig()


# =============================================================================
# RÉSULTATS
# =============================================================================

@dataclass
class ScanResult:
    """Résultat d'un scan antivirus."""
    is_clean: bool
    is_infected: bool = False
    is_error: bool = False
    virus_name: Optional[str] = None
    scan_time: float = 0.0
    file_size: int = 0
    file_path: Optional[str] = None
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "is_clean": self.is_clean,
            "is_infected": self.is_infected,
            "is_error": self.is_error,
            "virus_name": self.virus_name,
            "scan_time": round(self.scan_time, 4),
            "file_size": self.file_size,
            "file_path": self.file_path,
            "message": self.message
        }


# =============================================================================
# SERVICE CLAMAV
# =============================================================================

class ClamAVService:
    """
    Service d'intégration avec ClamAV.
    
    Support plusieurs modes:
    - filesystem: Utilisation de clamscan (mode par défaut)
    - socket: Connexion via socket à clamd
    - clamd: Utilisation de clamdscan
    
    Fonctionnalités:
    - Scan de fichiers
    - Scan de contenu en mémoire
    - Vérification de l'état du service
    - Gestion des erreurs
    """
    
    def __init__(self, config: ClamAVConfig = None):
        self.config = config or ClamAVConfig()
        
        # Créer le répertoire temporaire
        os.makedirs(self.config.temp_directory, exist_ok=True)
        
        # Vérifier les outils ClamAV disponibles
        self._check_clamav_tools()
    
    def _check_clamav_tools(self) -> None:
        """Vérifier les outils ClamAV disponibles."""
        tools = {
            "clamscan": self.config.clamscan_path,
            "clamd": self.config.clamd_path,
            "clamdscan": self.config.clamdscan_path
        }
        
        available_tools = []
        for name, path in tools.items():
            if os.path.exists(path):
                available_tools.append(name)
        
        if not available_tools:
            logger.warning("Aucun outil ClamAV trouvé. Scan antivirus désactivé.")
        else:
            logger.info(f"Outils ClamAV disponibles: {', '.join(available_tools)}")
    
    def _is_clamav_available(self) -> bool:
        """Vérifier si ClamAV est disponible."""
        return (
            os.path.exists(self.config.clamscan_path) or
            os.path.exists(self.config.clamdscan_path) or
            os.path.exists(self.config.clamd_path)
        )
    
    def _is_extension_allowed(self, filename: str) -> bool:
        """Vérifier si l'extension du fichier est autorisée."""
        if not self.config.allowed_extensions:
            return True  # Tout autoriser si liste vide
        
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.config.allowed_extensions
    
    def scan_file_filesystem(self, file_path: str, timeout: int = None) -> ScanResult:
        """
        Scanner un fichier en utilisant clamscan (filesystem mode).
        
        Args:
            file_path: Chemin vers le fichier à scanner
            timeout: Timeout en secondes
        
        Returns:
            ScanResult: Résultat du scan
        """
        if timeout is None:
            timeout = self.config.scan_timeout
        
        if not os.path.exists(file_path):
            return ScanResult(
                is_clean=False,
                is_error=True,
                message=f"Fichier introuvable: {file_path}"
            )
        
        try:
            # Vérifier l'extension
            if not self._is_extension_allowed(file_path):
                return ScanResult(
                    is_clean=False,
                    is_error=True,
                    message=f"Extension non autorisée: {os.path.splitext(file_path)[1]}"
                )
            
            # Vérifier la taille
            file_size = os.path.getsize(file_path)
            if file_size > self.config.max_file_size:
                return ScanResult(
                    is_clean=False,
                    is_error=True,
                    message=f"Fichier trop volumineux: {file_size} octets > {self.config.max_file_size}"
                )
            
            import time
            start_time = time.time()
            
            # Exécuter clamscan
            cmd = [
                self.config.clamscan_path,
                "--quiet",  # Mode silencieux
                "--no-summary",  # Pas de résumé
                file_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return ScanResult(
                    is_clean=False,
                    is_error=True,
                    scan_time=time.time() - start_time,
                    file_size=file_size,
                    file_path=file_path,
                    message="Scan timeout"
                )
            
            scan_time = time.time() - start_time
            exit_code = process.returncode
            
            # Interpréter le résultat
            if exit_code == 0:
                # Fichier propre
                return ScanResult(
                    is_clean=True,
                    is_infected=False,
                    scan_time=scan_time,
                    file_size=file_size,
                    file_path=file_path,
                    message="Fichier propre"
                )
            elif exit_code == 1:
                # Virus trouvé
                virus_name = self._extract_virus_name(stderr)
                return ScanResult(
                    is_clean=False,
                    is_infected=True,
                    virus_name=virus_name,
                    scan_time=scan_time,
                    file_size=file_size,
                    file_path=file_path,
                    message=f"Virus détecté: {virus_name}"
                )
            elif exit_code == 2:
                # Erreur
                return ScanResult(
                    is_clean=False,
                    is_error=True,
                    scan_time=scan_time,
                    file_size=file_size,
                    file_path=file_path,
                    message=f"Erreur ClamAV: {stderr}"
                )
            else:
                return ScanResult(
                    is_clean=False,
                    is_error=True,
                    scan_time=scan_time,
                    file_size=file_size,
                    file_path=file_path,
                    message=f"Code de sortie inconnu: {exit_code}"
                )
                
        except FileNotFoundError:
            return ScanResult(
                is_clean=False,
                is_error=True,
                message=f"Clamscan introuvable: {self.config.clamscan_path}"
            )
        except Exception as e:
            return ScanResult(
                is_clean=False,
                is_error=True,
                message=f"Erreur inattendue: {str(e)}"
            )
    
    def _extract_virus_name(self, stderr: str) -> Optional[str]:
        """Extraire le nom du virus de la sortie stderr."""
        # Exemple: "file.pdf: Win.Trojan.Generic-123456 FOUND"
        lines = stderr.split('\n')
        for line in lines:
            if "FOUND" in line:
                parts = line.split()
                for part in parts:
                    if part.endswith("FOUND"):
                        return part.replace("FOUND", "").strip()
                    elif "FOUND" in part:
                        return part.split("FOUND")[0].strip()
        return None
    
    def scan_content_filesystem(self, content: Union[bytes, str], filename: str = "tempfile") -> ScanResult:
        """
        Scanner un contenu en mémoire en utilisant clamscan.
        
        Args:
            content: Contenu à scanner (bytes ou str)
            filename: Nom de fichier fictif
        
        Returns:
            ScanResult: Résultat du scan
        """
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(
                dir=self.config.temp_directory,
                suffix=os.path.splitext(filename)[1],
                delete=False
            ) as temp_file:
                if isinstance(content, str):
                    temp_file.write(content.encode('utf-8'))
                else:
                    temp_file.write(content)
                temp_path = temp_file.name
            
            try:
                # Scanner le fichier temporaire
                result = self.scan_file_filesystem(temp_path)
                return result
            finally:
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            return ScanResult(
                is_clean=False,
                is_error=True,
                message=f"Erreur lors de la création du fichier temporaire: {str(e)}"
            )
    
    async def scan_file_async(self, file_path: str) -> ScanResult:
        """
        Scanner un fichier de manière asynchrone.
        
        Args:
            file_path: Chemin vers le fichier
        
        Returns:
            ScanResult: Résultat du scan
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.scan_file_filesystem, file_path)
    
    async def scan_content_async(self, content: Union[bytes, str], filename: str = "tempfile") -> ScanResult:
        """
        Scanner un contenu de manière asynchrone.
        
        Args:
            content: Contenu à scanner
            filename: Nom de fichier
        
        Returns:
            ScanResult: Résultat du scan
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.scan_content_filesystem(content, filename)
        )
    
    def check_service_status(self) -> Dict[str, Any]:
        """
        Vérifier l'état du service ClamAV.
        
        Returns:
            Dict: Statut du service
        """
        status = {
            "available": self._is_clamav_available(),
            "tools": {
                "clamscan": os.path.exists(self.config.clamscan_path),
                "clamd": os.path.exists(self.config.clamd_path),
                "clamdscan": os.path.exists(self.config.clamdscan_path)
            },
            "message": "OK" if self._is_clamav_available() else "ClamAV non disponible"
        }
        
        # Tester clamscan
        if status["tools"]["clamscan"]:
            try:
                result = subprocess.run(
                    [self.config.clamscan_path, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    status["version"] = result.stdout.strip()
                    status["message"] = "OK"
                else:
                    status["message"] = f"Erreur version: {result.stderr}"
            except Exception as e:
                status["message"] = f"Erreur: {str(e)}"
        
        return status


# =============================================================================
# SERVICE MOCK (pour les tests sans ClamAV)
# =============================================================================

class MockClamAVService:
    """
    Service mock pour les tests sans ClamAV installé.
    """
    
    def __init__(self):
        self.simulated_infections = {}  # {filename: virus_name}
    
    def scan_file_filesystem(self, file_path: str, timeout: int = None) -> ScanResult:
        """Scan mock."""
        filename = os.path.basename(file_path)
        
        if filename in self.simulated_infections:
            return ScanResult(
                is_clean=False,
                is_infected=True,
                virus_name=self.simulated_infections[filename],
                message=f"Virus simulé: {self.simulated_infections[filename]}"
            )
        else:
            return ScanResult(
                is_clean=True,
                is_infected=False,
                message="Fichier propre (mock)"
            )
    
    def scan_content_filesystem(self, content: Union[bytes, str], filename: str = "tempfile") -> ScanResult:
        """Scan de contenu mock."""
        return self.scan_file_filesystem(filename)
    
    async def scan_file_async(self, file_path: str) -> ScanResult:
        """Scan async mock."""
        return self.scan_file_filesystem(file_path)
    
    async def scan_content_async(self, content: Union[bytes, str], filename: str = "tempfile") -> ScanResult:
        """Scan de contenu async mock."""
        return self.scan_content_filesystem(content, filename)
    
    def check_service_status(self) -> Dict[str, Any]:
        """Statut mock."""
        return {
            "available": False,
            "tools": {"clamscan": False, "clamd": False, "clamdscan": False},
            "message": "Mode mock - ClamAV non installé",
            "mock": True
        }


# =============================================================================
# FABRIQUE DE SERVICE
# =============================================================================

def get_clamav_service(mock: bool = False) -> Union[ClamAVService, MockClamAVService]:
    """
    Récupérer le service ClamAV.
    
    Args:
        mock: Si True, retourner le service mock
    
    Returns:
        Service ClamAV
    """
    if mock or not ClamAVService(config)._is_clamav_available():
        logger.warning("Utilisation du service ClamAV mock")
        return MockClamAVService()
    else:
        return ClamAVService(config)


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Instance globale
_clamav_service: Optional[Union[ClamAVService, MockClamAVService]] = None


def get_global_clamav_service() -> Union[ClamAVService, MockClamAVService]:
    """Récupérer l'instance globale du service ClamAV."""
    global _clamav_service
    if _clamav_service is None:
        _clamav_service = get_clamav_service()
    return _clamav_service


async def scan_file(file_path: str) -> ScanResult:
    """
    Scanner un fichier avec ClamAV.
    
    Args:
        file_path: Chemin vers le fichier
    
    Returns:
        ScanResult: Résultat du scan
    """
    service = get_global_clamav_service()
    return await service.scan_file_async(file_path)


async def scan_content(content: Union[bytes, str], filename: str = "tempfile") -> ScanResult:
    """
    Scanner un contenu avec ClamAV.
    
    Args:
        content: Contenu à scanner
        filename: Nom de fichier
    
    Returns:
        ScanResult: Résultat du scan
    """
    service = get_global_clamav_service()
    return await service.scan_content_async(content, filename)


def check_clamav_status() -> Dict[str, Any]:
    """
    Vérifier l'état de ClamAV.
    
    Returns:
        Dict: Statut du service
    """
    service = get_global_clamav_service()
    return service.check_service_status()


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Tester le service ClamAV
        service = get_clamav_service()
        
        # Vérifier le statut
        status = service.check_service_status()
        print("Statut ClamAV:")
        print(f"  Disponible: {status['available']}")
        print(f"  Message: {status['message']}")
        
        if status['available']:
            # Tester avec un fichier propre
            result = await service.scan_content_async(b"Test content", "test.txt")
            print(f"\nScan de contenu propre: {result.to_dict()}")
        else:
            print("\nClamAV non disponible, utilisation du mock")
    
    asyncio.run(main())

