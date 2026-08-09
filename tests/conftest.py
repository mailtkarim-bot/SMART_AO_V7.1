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
# FIXTURES POUR AUTHENTIFICATION (P1-7 FIX)
# =============================================================================
# Deux approches pour les tests :
# 1. override_auth_dependency: Mock l'utilisateur (PATRON) pour les tests simples
# 2. Token JWT réels: Utiliser patron_token, conducteur_travaux_token, etc.
#    pour les tests RBAC qui nécessitent de vérifier les vraies permissions
# 
# NOTE: Le fixture override_auth_dependency N'EST PAS autouse, il doit être
# explicitement utilisé. Les tests RBAC doivent utiliser de vrais tokens.
# Voir test_rbac_security.py pour un exemple.

import pytest
from app.main import app
from app.core.auth import get_current_user
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


@pytest.fixture
def override_auth_dependency():
    """
    Surcharge get_current_user pour les tests qui n'ont pas besoin d'authentification réelle.
    
    NOTE: Ne pas utiliser ce fixture pour les tests RBAC !
    Utiliser à la place les fixtures patron_token, conducteur_travaux_token, etc.
    avec de vrais tokens JWT et l'endpoint /api/v1/finance/marge/brute ou autres.
    
    Voir test_rbac_security.py pour un exemple de tests RBAC sans override.
    """
    app.dependency_overrides[get_current_user] = _mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# =============================================================================
# FIXTURES POUR TESTS D'INTEGRATION AVEC AUTHENTIFICATION REELLE
# =============================================================================

@pytest.fixture
def client():
    """Client HTTP synchrone pour les tests d'intégration."""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture
def patron_token():
    """Token JWT pour un utilisateur PATRON."""
    from app.core.auth import create_access_token
    return create_access_token({
        "sub": "patron-test",
        "user_id": "patron-test",
        "role": "patron",
        "email": "patron@test.com",
    })


@pytest.fixture
def conducteur_travaux_token():
    """Token JWT pour un utilisateur CONDUCTEUR_TRAVAUX."""
    from app.core.auth import create_access_token
    return create_access_token({
        "sub": "conducteur-test",
        "user_id": "conducteur-test",
        "role": "conducteur_travaux",
        "email": "conducteur@test.com",
    })


@pytest.fixture
def charge_etudes_token():
    """Token JWT pour un utilisateur CHARGE_ETUDES."""
    from app.core.auth import create_access_token
    return create_access_token({
        "sub": "charge-etudes-test",
        "user_id": "charge-etudes-test",
        "role": "charge_etudes",
        "email": "charge.etudes@test.com",
    })
