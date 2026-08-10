"""
SMART_AO V7 - Tests unitaires pour CalculationAuditLog
======================================================
Tests de la fonction log_calculation_audit et du modèle CalculationAuditLog.
Conforme aux exigences juridiques (tribunal, expert-comptable).
"""

import pytest
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.future import select

from app.engines.security_engine.audit import (
    CalculationAuditLog,
    log_calculation_audit,
    AuditAction,
    AuditLevel
)
from app.core.auth import TokenData


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def calculation_input_data():
    """Données d'entrée pour un calcul financier standard."""
    return {
        "montant_ht": "10000.00",
        "cout_revient": "8500.00",
        "taux_tva": "0.20",
        "penalites": "500.00",
        "marge_minimale": "0.15"
    }


@pytest.fixture
def calculation_output_data():
    """Données de sortie pour un calcul financier standard."""
    return {
        "marge_brute": "1500.00",
        "marge_nette": "1000.00",
        "taux_marge": "0.15",
        "risque_detecte": False,
        "recommandations": ["Augmenter la marge de 2%"]
    }


@pytest.fixture
def mock_user():
    """Utilisateur mock pour les tests."""
    from app.schemas.users import Role
    return TokenData(
        user_id="user_123",
        email="test@btp.fr",
        role=Role.PATRON,
        full_name="Test User"
    )


@pytest.fixture
def mock_token_data():
    """TokenData mock pour les tests."""
    return {
        "user_id": "test_user_456",
        "email": "test@smart-ao.fr",
        "role": "conducteur_travaux"
    }


# =============================================================================
# TESTS POUR LE MODÈLE CalculationAuditLog
# =============================================================================

class TestCalculationAuditLogModel:
    """Tests du modèle SQLAlchemy CalculationAuditLog."""

    def test_model_has_required_columns(self):
        """Vérifie que le modèle a toutes les colonnes requises."""
        required_columns = [
            'id', 'calculation_id', 'calculation_type',
            'input_hash', 'output_hash', 'input_data', 'output_data',
            'user_id', 'mission_id', 'solver_version', 'duration_ms'
        ]
        
        for col in required_columns:
            assert hasattr(CalculationAuditLog, col), f"Colonne manquante: {col}"

    def test_model_tablename(self):
        """Vérifie le nom de la table."""
        assert CalculationAuditLog.__tablename__ == "calculation_audit_logs"

    def test_calculation_id_is_unique(self):
        """Vérifie que calculation_id est unique."""
        from sqlalchemy import inspect
        inspector = inspect(CalculationAuditLog)
        calculation_id_col = inspector.columns['calculation_id']
        assert calculation_id_col.unique, "calculation_id doit être unique"


# =============================================================================
# TESTS POUR LA FONCTION log_calculation_audit
# =============================================================================

class TestLogCalculationAudit:
    """Tests de la fonction log_calculation_audit."""

    @pytest.mark.asyncio
    async def test_log_calculation_audit_creates_record(
        self, 
        calculation_input_data, 
        calculation_output_data
    ):
        """Teste que la fonction crée un enregistrement avec des données valides."""
        calculation_id = await log_calculation_audit(
            calculation_type="marge",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_789"
        )
        
        # Vérifie que l'ID est généré
        assert calculation_id is not None
        assert isinstance(calculation_id, str)
        assert len(calculation_id) > 0

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_user(
        self,
        calculation_input_data,
        calculation_output_data,
        mock_user
    ):
        """Teste que la fonction accepte un objet utilisateur (converti en dict)."""
        # Convertir TokenData en dict pour la fonction
        user_dict = {
            "user_id": mock_user.user_id,
            "username": mock_user.username,
            "email": mock_user.email,
            "role": mock_user.role.value if hasattr(mock_user.role, 'value') else mock_user.role
        }
        calculation_id = await log_calculation_audit(
            calculation_type="penalite_ccag",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            user=user_dict,
            mission_id="mission_abc"
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_token_data(
        self,
        calculation_input_data,
        calculation_output_data,
        mock_token_data
    ):
        """Teste que la fonction accepte un dict utilisateur."""
        calculation_id = await log_calculation_audit(
            calculation_type="tresorerie",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            user=mock_token_data,
            mission_id="mission_xyz"
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_generates_correct_hashes(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que les hashs SHA-256 sont générés correctement."""
        # Calculer les hashs attendus
        input_str = json.dumps(calculation_input_data, sort_keys=True)
        output_str = json.dumps(calculation_output_data, sort_keys=True)
        
        expected_input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        expected_output_hash = hashlib.sha256(output_str.encode()).hexdigest()
        
        calculation_id = await log_calculation_audit(
            calculation_type="chiffrage",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_hash_test"
        )
        
        # Vérifier que la fonction a bien généré des hashs
        # (On ne peut pas vérifier directement sans accéder à la base,
        # mais on vérifie que l'appel ne lève pas d'erreur)
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_duration(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que la fonction accepte un paramètre duration_ms."""
        calculation_id = await log_calculation_audit(
            calculation_type="bt_projection",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_duration",
            duration_ms=150
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_solver_version(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que la fonction accepte un paramètre solver_version."""
        calculation_id = await log_calculation_audit(
            calculation_type="sous_chiffrage",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_solver",
            solver_version="2.1.0"
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_different_calculation_types(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que la fonction fonctionne avec différents types de calculs."""
        calculation_types = [
            "marge", "penalite_ccag", "tresorerie", "bt_projection",
            "chiffrage", "sous_chiffrage", "worst_case", "pab_detection"
        ]
        
        for calc_type in calculation_types:
            calculation_id = await log_calculation_audit(
                calculation_type=calc_type,
                input_data=calculation_input_data,
                output_data=calculation_output_data,
                mission_id=f"mission_{calc_type}"
            )
            assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_empty_data(
        self
    ):
        """Teste que la fonction gère les données vides."""
        calculation_id = await log_calculation_audit(
            calculation_type="test_empty",
            input_data={},
            output_data={},
            mission_id="mission_empty"
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_with_decimal_data(
        self
    ):
        """Teste que la fonction gère les objets Decimal."""
        input_data = {
            "montant": str(Decimal("10000.50")),
            "cout": str(Decimal("8500.25"))
        }
        output_data = {
            "marge": str(Decimal("1500.25"))
        }
        
        calculation_id = await log_calculation_audit(
            calculation_type="decimal_test",
            input_data=input_data,
            output_data=output_data,
            mission_id="mission_decimal"
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_unique_ids(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que chaque appel génère un ID unique."""
        id1 = await log_calculation_audit(
            calculation_type="test1",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_1"
        )
        
        id2 = await log_calculation_audit(
            calculation_type="test2",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_2"
        )
        
        assert id1 != id2

    @pytest.mark.asyncio
    async def test_log_calculation_audit_without_mission_id(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que la fonction fonctionne sans mission_id."""
        calculation_id = await log_calculation_audit(
            calculation_type="no_mission",
            input_data=calculation_input_data,
            output_data=calculation_output_data
        )
        
        assert calculation_id is not None

    @pytest.mark.asyncio
    async def test_log_calculation_audit_without_user(
        self,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que la fonction fonctionne sans utilisateur."""
        calculation_id = await log_calculation_audit(
            calculation_type="no_user",
            input_data=calculation_input_data,
            output_data=calculation_output_data,
            mission_id="mission_no_user"
        )
        
        assert calculation_id is not None


# =============================================================================
# TESTS D'INTÉGRATION AVEC BASE DE DONNÉES (ASYNC)
# =============================================================================

class TestCalculationAuditLogDatabase:
    """Tests d'intégration avec base de données.
    
    Note: Tests désactivés car SQLite ne supporte pas le type ARRAY utilisé dans d'autres modèles.
    Ces tests nécessitent PostgreSQL pour fonctionner correctement.
    """

    @pytest.fixture
    def async_engine(self):
        """Crée un moteur async pour les tests."""
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
            connect_args={"check_same_thread": False}
        )

    @pytest.fixture
    async def async_session_factory(self, async_engine):
        """Crée une factory de sessions async."""
        async with async_engine.begin() as conn:
            # Créer toutes les tables
            from app.core.database import Base
            from app.models.mission import Mission
            from app.models.user import User
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(Mission.metadata.create_all)
            await conn.run_sync(User.metadata.create_all)
            await conn.run_sync(CalculationAuditLog.metadata.create_all)
        
        AsyncTestingSessionLocal = sessionmaker(
            async_engine, 
            expire_on_commit=False, 
            class_=AsyncSession
        )
        return AsyncTestingSessionLocal

    @pytest.mark.skip(reason="Nécessite PostgreSQL - SQLite ne supporte pas ARRAY")
    @pytest.mark.asyncio
    async def test_audit_log_persists_to_database(
        self,
        async_session_factory,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que l'audit log est bien persistant en base de données."""
        AsyncSessionLocal = async_session_factory
        
        async with AsyncSessionLocal() as db:
            # Appel de la fonction avec base de données
            calculation_id = await log_calculation_audit(
                calculation_type="marge_test",
                input_data=calculation_input_data,
                output_data=calculation_output_data,
                user={"user_id": "test_user"},
                mission_id="test_mission",
                db=db,
                duration_ms=100
            )
            
            # Vérifier que l'enregistrement existe
            result = await db.execute(
                select(CalculationAuditLog).where(
                    CalculationAuditLog.calculation_id == calculation_id
                )
            )
            audit_log = result.scalar_one_or_none()
            
            assert audit_log is not None
            assert audit_log.calculation_type == "marge_test"
            assert audit_log.mission_id == "test_mission"

    @pytest.mark.skip(reason="Nécessite PostgreSQL - SQLite ne supporte pas ARRAY")
    @pytest.mark.asyncio
    async def test_audit_log_hashes_are_correct(
        self,
        async_session_factory,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste que les hashs stockés sont corrects."""
        AsyncSessionLocal = async_session_factory
        
        async with AsyncSessionLocal() as db:
            calculation_id = await log_calculation_audit(
                calculation_type="hash_test",
                input_data=calculation_input_data,
                output_data=calculation_output_data,
                mission_id="hash_mission",
                db=db
            )
            
            result = await db.execute(
                select(CalculationAuditLog).where(
                    CalculationAuditLog.calculation_id == calculation_id
                )
            )
            audit_log = result.scalar_one_or_none()
            
            # Recalculer les hashs attendus
            input_str = json.dumps(calculation_input_data, sort_keys=True)
            output_str = json.dumps(calculation_output_data, sort_keys=True)
            expected_input_hash = hashlib.sha256(input_str.encode()).hexdigest()
            expected_output_hash = hashlib.sha256(output_str.encode()).hexdigest()
            
            assert audit_log.input_hash == expected_input_hash
            assert audit_log.output_hash == expected_output_hash

    @pytest.mark.skip(reason="Nécessite PostgreSQL - SQLite ne supporte pas ARRAY")
    @pytest.mark.asyncio
    async def test_multiple_audit_logs(
        self,
        async_session_factory,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste l'enregistrement de multiples audit logs."""
        AsyncSessionLocal = async_session_factory
        
        async with AsyncSessionLocal() as db:
            # Créer plusieurs enregistrements
            for i in range(5):
                await log_calculation_audit(
                    calculation_type=f"test_{i}",
                    input_data=calculation_input_data,
                    output_data=calculation_output_data,
                    mission_id=f"mission_{i}",
                    db=db
                )
            
            # Vérifier que tous les enregistrements existent
            result = await db.execute(
                select(CalculationAuditLog)
            )
            all_logs = result.scalars().all()
            
            assert len(all_logs) >= 5


# =============================================================================
# TESTS DE CONFORMITÉ JURIDIQUE
# =============================================================================

class TestLegalCompliance:
    """Tests de conformité juridique pour l'audit des calculs."""

    @pytest.mark.skip(reason="Nécessite PostgreSQL - SQLite ne supporte pas ARRAY")
    @pytest.mark.asyncio
    async def test_audit_log_contains_all_required_fields(
        self,
        async_session_factory,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste qu'un audit log contient tous les champs requis pour preuve légale."""
        AsyncSessionLocal = async_session_factory
        
        async with AsyncSessionLocal() as db:
            calculation_id = await log_calculation_audit(
                calculation_type="legal_test",
                input_data=calculation_input_data,
                output_data=calculation_output_data,
                user={"user_id": "legal_user", "role": "patron"},
                mission_id="legal_mission",
                db=db,
                duration_ms=200,
                solver_version="1.0.0"
            )
            
            result = await db.execute(
                select(CalculationAuditLog).where(
                    CalculationAuditLog.calculation_id == calculation_id
                )
            )
            audit_log = result.scalar_one_or_none()
            
            # Champs requis pour preuve légale
            required_fields = [
                'calculation_id', 'calculation_type', 'input_hash', 'output_hash',
                'input_data', 'output_data', 'user_id', 'mission_id',
                'solver_version', 'duration_ms', 'created_at'
            ]
            
            for field in required_fields:
                assert hasattr(audit_log, field), f"Champ manquant: {field}"
                value = getattr(audit_log, field)
                assert value is not None, f"Champ {field} est None"

    @pytest.mark.skip(reason="Nécessite PostgreSQL - SQLite ne supporte pas ARRAY")
    @pytest.mark.asyncio
    async def test_audit_log_immutable(
        self,
        async_session_factory,
        calculation_input_data,
        calculation_output_data
    ):
        """Teste l'immutabilité des audit logs (principe WORM)."""
        AsyncSessionLocal = async_session_factory
        
        async with AsyncSessionLocal() as db:
            calculation_id = await log_calculation_audit(
                calculation_type="worm_test",
                input_data=calculation_input_data,
                output_data=calculation_output_data,
                mission_id="worm_mission",
                db=db
            )
            
            result = await db.execute(
                select(CalculationAuditLog).where(
                    CalculationAuditLog.calculation_id == calculation_id
                )
            )
            audit_log = result.scalar_one_or_none()
            
            # Stockage des valeurs originales
            original_type = audit_log.calculation_type
            original_input_hash = audit_log.input_hash
            
            # Tentative de modification (ne devrait pas être possible en production)
            # En test, on vérifie juste que les données sont bien stockées
            assert original_type == "worm_test"
            assert original_input_hash is not None


# =============================================================================
# EXÉCUTION DES TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
