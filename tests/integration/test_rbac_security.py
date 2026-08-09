"""
SMART_AO V7 - Tests RBAC Security
==================================
Tests d'intrusion RBAC pour vérifier que seuls les utilisateurs autorisés
peuvent accéder aux endpoints financiers et documents sensibles.

Ces tests vérifient:
1. Que require_financial_access bloque les rôles non-autorisés
2. Que l'endpoint /financiere est protégé doublement (RBAC + require_financial_access)
3. Que les endpoints RAG sont protégés
4. Que les endpoints finance_advanced sont protégés
"""

import asyncio
import pytest
from fastapi import status
from typing import Dict, Any

from app.main import app
from app.core.auth import get_current_user, get_password_hash
from app.core.database import engine, Base
from app.models.user import User
from app.engines.security_engine.rbac import Role


@pytest.fixture(autouse=True)
def _disable_auth_override_for_rbac():
    """Pour les tests RBAC, on utilise l'authentification JWT réelle."""
    app.dependency_overrides.pop(get_current_user, None)
    yield


async def _create_rbac_users():
    """Crée les utilisateurs de test RBAC en base."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine) as session:
        users = [
            User(
                user_id="patron-test",
                email="patron@test.com",
                username="patron_test",
                full_name="Patron Test",
                role=Role.PATRON,
                hashed_password=get_password_hash("test"),
                is_active=True,
            ),
            User(
                user_id="conducteur-test",
                email="conducteur@test.com",
                username="conducteur_test",
                full_name="Conducteur Test",
                role=Role.CONDUCTEUR_TRAVAUX,
                hashed_password=get_password_hash("test"),
                is_active=True,
            ),
            User(
                user_id="charge-etudes-test",
                email="charge.etudes@test.com",
                username="charge_etudes_test",
                full_name="Charge Etudes Test",
                role=Role.CHARGE_ETUDES,
                hashed_password=get_password_hash("test"),
                is_active=True,
            ),
        ]
        for user in users:
            session.add(user)
        await session.commit()


@pytest.fixture(scope="module", autouse=True)
def rbac_test_users():
    """Fixture module-scoped qui initialise les utilisateurs RBAC en base."""
    asyncio.run(_create_rbac_users())
    yield


class TestRBACFinancialAccess:
    """Tests pour la protection des accès financiers."""
    
    def test_require_financial_access_allows_patron(self, client, patron_token):
        """Le rôle PATRON doit pouvoir accéder aux données financières."""
        headers = {"Authorization": f"Bearer {patron_token}"}

        # Test sur un endpoint financier existant (/marge/brute)
        response = client.post(
            "/api/v1/finance/marge/brute",
            headers=headers,
            json={"montant_marche": 500000, "cout_reel": 400000}
        )

        # Doit réussir ou échouer pour d'autres raisons (pas 403)
        assert response.status_code != status.HTTP_403_FORBIDDEN, \
            f"PATRON ne devrait pas être bloqué par require_financial_access (got {response.status_code})"
    
    def test_require_financial_access_blocks_conducteur_travaux(self, client, conducteur_travaux_token):
        """Le rôle CONDUCTEUR_TRAVAUX doit être bloqué des données financières."""
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}

        # Test sur un endpoint financier existant (/marge/brute)
        response = client.post(
            "/api/v1/finance/marge/brute",
            headers=headers,
            json={"montant_marche": 500000, "cout_reel": 400000}
        )

        # Doit être bloqué avec 403
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            f"CONDUCTEUR_TRAVAUX doit être bloqué des données financières (got {response.status_code})"

        # Vérifier le message d'erreur
        assert "Financial data requires PATRON role" in response.json().get("detail", "")


class TestEnveloppeFinanciereProtection:
    """Tests pour la protection de l'enveloppe FINANCIERE."""
    
    def test_enveloppe_financiere_blocks_non_admin(self, client, conducteur_travaux_token):
        """L'endpoint /financiere doit bloquer les non-admins."""
        mission_id = "test-mission-123"
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}
        
        response = client.get(f"/api/v1/enveloppes/{mission_id}/financiere", headers=headers)
        
        # Doit être bloqué (403)
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "L'enveloppe FINANCIERE doit être protégée pour les non-admins"
    
    def test_enveloppe_financiere_requires_double_auth(self, client, patron_token):
        """L'endpoint /financiere doit avoir une double protection RBAC + require_financial_access."""
        mission_id = "test-mission-123"
        headers = {"Authorization": f"Bearer {patron_token}"}
        
        response = client.get(f"/api/v1/enveloppes/{mission_id}/financiere", headers=headers)
        
        # Même PATRON peut échouer si l'enveloppe n'existe pas (404), mais pas 403
        if response.status_code == status.HTTP_403_FORBIDDEN:
            pytest.fail("PATRON ne devrait pas être bloqué par require_financial_access")


class TestRAGProtection:
    """Tests pour la protection des endpoints RAG."""
    
    def test_rag_index_blocks_non_financial(self, client, conducteur_travaux_token):
        """L'endpoint RAG /index doit bloquer les utilisateurs sans accès financier."""
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}
        
        # Tentative d'upload sans accès financier
        response = client.post(
            "/api/v1/rag/index",
            headers=headers,
            files={"file": ("test.pdf", b"dummy content", "application/pdf")}
        )
        
        # Doit être bloqué
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "RAG index doit être protégé par require_financial_access"
    
    def test_rag_search_blocks_non_financial(self, client, conducteur_travaux_token):
        """L'endpoint RAG /search doit bloquer les utilisateurs sans accès financier."""
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}
        
        response = client.get("/api/v1/rag/search?query=test", headers=headers)
        
        # Doit être bloqué
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "RAG search doit être protégé par require_financial_access"


class TestFinanceAdvancedProtection:
    """Tests pour la protection des endpoints finance_advanced."""
    
    def test_finance_advanced_optimiser_blocks_non_financial(self, client, conducteur_travaux_token):
        """L'endpoint /chiffrage/optimiser doit bloquer les non-financiers."""
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}
        
        payload = {
            "ressources": [],
            "taches": []
        }
        
        response = client.post(
            "/api/v1/finance/advanced/chiffrage/optimiser",
            json=payload,
            headers=headers
        )
        
        # Doit être bloqué
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "finance_advanced/chiffrage/optimiser doit être protégé"
    
    def test_finance_advanced_simulation_blocks_non_financial(self, client, conducteur_travaux_token):
        """L'endpoint /simulation/chantier doit bloquer les non-financiers."""
        headers = {"Authorization": f"Bearer {conducteur_travaux_token}"}
        
        payload = {
            "montant_marche": 100000,
            "duree_mois": 12
        }
        
        response = client.post(
            "/api/v1/finance/advanced/simulation/chantier",
            json=payload,
            headers=headers
        )
        
        # Doit être bloqué
        assert response.status_code == status.HTTP_403_FORBIDDEN, \
            "finance_advanced/simulation/chantier doit être protégé"


class TestRBACMatrix:
    """Tests pour la matrice RBAC des enveloppes."""
    
    def test_salarie_cannot_read_financiere(self):
        """Un SALARIE ne doit avoir AUCUNE permission sur FINANCIERE."""
        from app.engines.security_engine.enveloppe_rbac import EnveloppeRBAC
        
        user_id = "test-salarie-123"
        context = {"user_role": "SALARIE"}
        
        # Doit retourner False
        assert not EnveloppeRBAC.can_read_enveloppe(user_id, "FINANCIERE", context), \
            "SALARIE ne doit pas pouvoir lire FINANCIERE"
        
        assert not EnveloppeRBAC.can_write_enveloppe(user_id, "FINANCIERE", context), \
            "SALARIE ne doit pas pouvoir écrire dans FINANCIERE"
        
        assert not EnveloppeRBAC.can_export_enveloppe(user_id, "FINANCIERE", context), \
            "SALARIE ne doit pas pouvoir exporter FINANCIERE"
    
    def test_admin_can_read_financiere(self):
        """Un ADMIN doit pouvoir lire FINANCIERE."""
        from app.engines.security_engine.enveloppe_rbac import EnveloppeRBAC
        
        user_id = "test-admin-123"
        context = {"user_role": "ADMIN"}
        
        # Doit retourner True
        assert EnveloppeRBAC.can_read_enveloppe(user_id, "FINANCIERE", context), \
            "ADMIN doit pouvoir lire FINANCIERE"
        
        assert EnveloppeRBAC.can_write_enveloppe(user_id, "FINANCIERE", context), \
            "ADMIN doit pouvoir écrire dans FINANCIERE"
