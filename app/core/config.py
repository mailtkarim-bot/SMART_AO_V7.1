"""
SMART_AO V7 - config.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Configuration
=============================
Configuration centrale avec Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration centrale SMART_AO V7."""
    
    # Application
    APP_NAME: str = "SMART_AO V7 Engine OS"
    APP_VERSION: str = "1.0.0"
    APP_ENVIRONMENT: str = "development"
    DEBUG: bool = False  # Désactivé par défaut pour la sécurité
    APP_LOG_LEVEL: str = "INFO"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_ROOT_PATH: str = "/api"
    API_RELOAD: bool = True
    
    # CORS - Sécurisé par défaut (à configurer en production)
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost", "http://localhost:3000", "http://localhost:8000"])
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])
    
    # Database - PAS DE VALEURS PAR DÉFAUT POUR LA PRODUCTION
    DATABASE_URL: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "vault_documents"
    
    # MinIO - PAS DE CRÉDENTIALES PAR DÉFAUT POUR LA PRODUCTION
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET: str = "smart-ao-documents"
    MINIO_SECURE: bool = False
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT Security
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # Alias pour compatibilité avec auth.py
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Circuit Breakers
    CB_ENABLED: bool = True
    CB_FAILURE_THRESHOLD: int = 5
    CB_SUCCESS_THRESHOLD: int = 2
    CB_TIMEOUT_SECONDS: int = 60
    CB_RESET_TIMEOUT_SECONDS: int = 300
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_BURST_SIZE: int = 50
    
    # Workflow
    WORKFLOW_MAX_CONCURRENT: int = 5
    WORKFLOW_TIMEOUT_MINUTES: int = 30
    WORKFLOW_RETRY_ATTEMPTS: int = 3
    WORKFLOW_RETRY_DELAY_SECONDS: int = 5
    
    # Agents
    AGENT_TIMEOUT_SECONDS: int = 120
    AGENT_MAX_RETRIES: int = 3
    AGENT_RETRY_DELAY_SECONDS: int = 2
    AGENT_CONCURRENT_EXECUTION: int = 5
    
    # Upload
    UPLOAD_MAX_SIZE_MB: int = 50
    UPLOAD_ALLOWED_EXTENSIONS: str = ".pdf,.docx,.xlsx,.txt,.json"
    UPLOAD_TEMP_DIRECTORY: str = "/tmp/uploads"
    UPLOAD_CLEANUP_AFTER_MINUTES: int = 60
    
    # Storage
    STORAGE_DATA_DIRECTORY: str = "./data"
    STORAGE_MAX_DOCUMENT_SIZE_MB: int = 100
    STORAGE_ENCRYPTION_ENABLED: bool = True  # Activé pour RGPD
    STORAGE_COMPRESSION_ENABLED: bool = True
    STORAGE_ENCRYPTION_KEY: Optional[str] = None  # Doit être fourni via .env
    
    # RBAC - Utilisateurs admin (par défaut)
    ADMIN_USERS: List[str] = ["admin", "noor"]
    
    # SMTP / Notification
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    SMTP_TLS: bool = True
    
    # MCP
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8080
    
    # UI
    UI_HOST: str = "0.0.0.0"
    UI_PORT: int = 8501
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignorer les variables d'environnement non définies dans le modèle
    )


@lru_cache()
def get_settings():
    """Récupérer les paramètres de configuration."""
    return Settings()


settings = get_settings()

