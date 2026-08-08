"""
SMART_AO V7 - logging.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Logging Structuré
=================================
Configuration centralisée du logging avec structlog.
Permet un logging structuré, coloré et filtrable.

Source: ENGINEERING-HANDBOOK_V7.md §7
"""

import structlog
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import os


def configure_structlog(
    level: str = "INFO",
    json_output: bool = False,
    colorize: bool = True,
    include_timestamp: bool = True,
    include_process: bool = True,
    include_thread: bool = True,
    log_file: Optional[str] = None
) -> structlog.BoundLogger:
    """
    Configure structlog avec les paramètres donnés.
    
    Args:
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Sortie au format JSON (utile pour ELK, etc.)
        colorize: Coloriser la sortie console
        include_timestamp: Inclure le timestamp
        include_process: Inclure le PID
        include_thread: Inclure le thread ID
        log_file: Fichier de log optionnel
    
    Returns:
        structlog.BoundLogger: Logger configuré
    """
    # Déterminer le niveau
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Processors pour structlog
    processors = []
    
    # Ajouter le timestamp
    if include_timestamp:
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    # Ajouter les infos standards
    if include_process:
        processors.append(structlog.processors.add_log_level)
        processors.append(_add_process_info)
    
    if include_thread:
        processors.append(_add_thread_info)
    
    # Format de sortie
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Format console coloré
        processors.append(structlog.processors.StackInfoRenderer())
        processors.append(structlog.processors.format_exc_info)
        if colorize:
            processors.append(_colorize_log)
        processors.append(structlog.dev.ConsoleRenderer(colors=colorize))
    
    # Configuration de base
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory() if not log_file else structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True
    )
    
    # Configuration du logger standard
    stdlib_logger = structlog.get_logger()
    stdlib_logger.setLevel(log_level)
    
    # Ajouter un handler fichier si spécifié
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        stdlib_logger.addHandler(file_handler)
    
    return stdlib_logger


def _add_process_info(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute les infos de processus au log."""
    event_dict['process'] = {
        'pid': os.getpid(),
        'name': os.path.basename(sys.argv[0])
    }
    return event_dict


def _add_thread_info(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute les infos de thread au log."""
    import threading
    event_dict['thread'] = {
        'id': threading.get_ident(),
        'name': threading.current_thread().name
    }
    return event_dict


def _colorize_log(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute des couleurs aux logs selon le niveau."""
    level = event_dict.get('level')
    
    if level == 'error' or level == 'critical':
        event_dict['_color'] = 'red'
    elif level == 'warning':
        event_dict['_color'] = 'yellow'
    elif level == 'info':
        event_dict['_color'] = 'blue'
    elif level == 'debug':
        event_dict['_color'] = 'cyan'
    
    return event_dict


# Configuration par défaut
def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Récupère un logger structlog avec la configuration par défaut.
    
    Args:
        name: Nom du logger (optionnel)
    
    Returns:
        structlog.BoundLogger: Logger prêt à l'emploi
    """
    # Vérifier si déjà configuré
    if not structlog.is_configured():
        configure_structlog(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            json_output=os.getenv('LOG_JSON', 'false').lower() == 'true',
            colorize=os.getenv('LOG_COLORIZE', 'true').lower() != 'false'
        )
    
    return structlog.get_logger(name or __name__)


# Logger global pour le projet
logger = get_logger("SMART_AO_V7")


# Utilitaires pour les logs contextuels
def log_with_context(logger: structlog.BoundLogger, context: Dict[str, Any]) -> structlog.BoundLogger:
    """
    Crée un logger avec un contexte pré-rempli.
    """
    return logger.bind(**context)


# Configuration au démarrage
if not structlog.is_configured():
    configure_structlog()

