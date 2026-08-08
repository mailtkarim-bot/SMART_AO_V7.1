"""
SMART_AO V7 - Conftest
======================
Configuration commune pour les tests.
"""

import os

# Forcer l'environnement de test pour désactiver le pooling SQLAlchemy
# (évite les conflits d'event loop avec TestClient + asyncpg)
os.environ["APP_ENVIRONMENT"] = "test"

# Clé JWT pour les tests — les tests doivent générer des tokens valides
# ou surcharger les dépendances d'authentification explicitement.
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-do-not-use-in-production"


# =============================================================================
# BYPASS AUTHENTIFICATION POUR LES TESTS
# =============================================================================
# L'option AUTH_DISABLED a été supprimée de la configuration de production.
# Pour les tests, on surcharge la dépendance get_current_user afin de ne pas
# multiplier la complexité des tests unitaires et d'intégration.

import pytest
from app.main import app
from app.core.security import get_current_user
from app.core.database import engine, Base


async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
def reset_test_database():
    """Recrée les tables de test proprement (single-tenant pur, sans colonne tenant_id)."""
    import asyncio
    asyncio.run(_reset_db())
    yield


async def _mock_get_current_user():
    """Utilisateur de test avec rôle PATRON pour couvrir tous les accès RBAC."""
    return {
        "user_id": "test_user",
        "role": "patron",
        "email": "test@example.com",
    }


@pytest.fixture(autouse=True)
def _override_auth_dependency():
    """Surcharge get_current_user pour l'ensemble de la suite de tests."""
    app.dependency_overrides[get_current_user] = _mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
