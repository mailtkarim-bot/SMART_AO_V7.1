"""
SMART_AO V7 - test_models_simple.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Unitaires Simples pour les Modèles
====================================================
Tests sans base de données pour les modèles SQLAlchemy
"""

import pytest
from datetime import datetime, timezone
from enum import Enum


# =============================================================================
# TESTS POUR app/models/events.py (sans DB)
# =============================================================================

class TestEventType:
    """Tests pour EventType Enum"""
    
    def test_event_type_enum_values(self):
        """Tester que toutes les valeurs de EventType sont présentes"""
        from app.models.events import EventType
        expected_types = [
            "MISSION_CREATED", "MISSION_STARTED", "MISSION_COMPLETED", "MISSION_FAILED",
            "STEP_STARTED", "STEP_COMPLETED", "STEP_FAILED",
            "DOCUMENT_UPLOADED", "DOCUMENT_PROCESSED",
            "AGENT_REGISTERED", "AGENT_EXECUTED",
            "SYSTEM_ERROR"
        ]
        for etype in expected_types:
            assert hasattr(EventType, etype)
            assert getattr(EventType, etype).value == etype
    
    def test_event_type_is_str_enum(self):
        """Tester que EventType hérite de str et Enum"""
        from app.models.events import EventType
        assert issubclass(EventType, str)
        assert issubclass(EventType, Enum)
    
    def test_event_type_all_values_accessible(self):
        """Tester l'accès à toutes les valeurs"""
        from app.models.events import EventType
        all_types = list(EventType)
        assert len(all_types) == 12
        assert EventType.MISSION_CREATED in all_types


class TestEventModel:
    """Tests pour le modèle Event sans DB"""
    
    def test_event_class_exists(self):
        """Tester que la classe Event existe"""
        from app.models.events import Event
        assert Event is not None
    
    def test_event_tablename(self):
        """Tester le nom de la table"""
        from app.models.events import Event
        assert Event.__tablename__ == "events"
    
    def test_event_has_required_attributes(self):
        """Tester que Event a tous les attributs requis"""
        from app.models.events import Event
        required_attrs = ['id', 'event_type', 'event_data', 'source', 'mission_id', 'step_id', 'created_at']
        for attr in required_attrs:
            assert hasattr(Event, attr)
    
    def test_event_repr_method_exists(self):
        """Tester que __repr__ existe"""
        from app.models.events import Event
        assert hasattr(Event, '__repr__')


class TestMissionEventModel:
    """Tests pour MissionEvent sans DB"""
    
    def test_mission_event_class_exists(self):
        """Tester que la classe MissionEvent existe"""
        from app.models.events import MissionEvent
        assert MissionEvent is not None
    
    def test_mission_event_tablename(self):
        """Tester le nom de la table"""
        from app.models.events import MissionEvent
        assert MissionEvent.__tablename__ == "mission_events"
    
    def test_mission_event_has_required_attributes(self):
        """Tester que MissionEvent a tous les attributs requis"""
        from app.models.events import MissionEvent
        required_attrs = ['id', 'mission_id', 'step_id', 'event_type', 'data', 'created_at']
        for attr in required_attrs:
            assert hasattr(MissionEvent, attr)


# =============================================================================
# TESTS POUR app/models/mission.py (sans DB)
# =============================================================================

class TestMissionStatus:
    """Tests pour MissionStatus Enum"""
    
    def test_mission_status_enum_values(self):
        """Tester que toutes les valeurs de MissionStatus sont présentes"""
        from app.models.mission import MissionStatus
        expected_statuses = [
            "CREATED", "PARSING", "EXTRACTING", "CLASSIFYING",
            "AGENT_RUNNING", "COMPILING", "REPORTING", "DONE", "FAILED"
        ]
        for status in expected_statuses:
            assert hasattr(MissionStatus, status)
            assert getattr(MissionStatus, status).value == status
    
    def test_mission_status_is_enum(self):
        """Tester que MissionStatus est un Enum"""
        from app.models.mission import MissionStatus
        assert issubclass(MissionStatus, Enum)


class TestMissionStepStatus:
    """Tests pour MissionStepStatus Enum"""
    
    def test_mission_step_status_enum_values(self):
        """Tester que toutes les valeurs de MissionStepStatus sont présentes"""
        from app.models.mission import MissionStepStatus
        expected_statuses = ["PENDING", "RUNNING", "DONE", "FAILED", "SKIPPED"]
        for status in expected_statuses:
            assert hasattr(MissionStepStatus, status)
            assert getattr(MissionStepStatus, status).value == status


class TestMissionModel:
    """Tests pour le modèle Mission sans DB"""
    
    def test_mission_class_exists(self):
        """Tester que la classe Mission existe"""
        from app.models.mission import Mission
        assert Mission is not None
    
    def test_mission_tablename(self):
        """Tester le nom de la table"""
        from app.models.mission import Mission
        assert Mission.__tablename__ == "missions"
    
    def test_mission_has_required_attributes(self):
        """Tester que Mission a tous les attributs requis"""
        from app.models.mission import Mission
        required_attrs = [
            'id', 'mission_id', 'name', 'description', 'status',
            'created_at', 'updated_at', 'completed_at', 'total_steps',
            'completed_steps', 'error_message', 'extra_metadata', 'project_id'
        ]
        for attr in required_attrs:
            assert hasattr(Mission, attr)
    
    def test_mission_has_progress_property(self):
        """Tester que Mission a la propriété progress"""
        from app.models.mission import Mission
        assert hasattr(Mission, 'progress')
    
    def test_mission_has_is_complete_property(self):
        """Tester que Mission a la propriété is_complete"""
        from app.models.mission import Mission
        assert hasattr(Mission, 'is_complete')
    
    def test_mission_has_is_failed_property(self):
        """Tester que Mission a la propriété is_failed"""
        from app.models.mission import Mission
        assert hasattr(Mission, 'is_failed')
    
    def test_mission_has_relationships(self):
        """Tester que Mission a les relations"""
        from app.models.mission import Mission
        assert hasattr(Mission, 'steps')
        assert hasattr(Mission, 'events')


class TestMissionStepModel:
    """Tests pour le modèle MissionStep sans DB"""
    
    def test_mission_step_class_exists(self):
        """Tester que la classe MissionStep existe"""
        from app.models.mission import MissionStep
        assert MissionStep is not None
    
    def test_mission_step_tablename(self):
        """Tester le nom de la table"""
        from app.models.mission import MissionStep
        assert MissionStep.__tablename__ == "mission_steps"
    
    def test_mission_step_has_required_attributes(self):
        """Tester que MissionStep a tous les attributs requis"""
        from app.models.mission import MissionStep
        required_attrs = [
            'id', 'mission_id', 'step_name', 'step_order', 'status',
            'input_data', 'output_data', 'error_message', 'started_at',
            'completed_at', 'agent_name', 'execution_time_ms'
        ]
        for attr in required_attrs:
            assert hasattr(MissionStep, attr)
    
    def test_mission_step_has_table_args(self):
        """Tester que MissionStep a __table_args__"""
        from app.models.mission import MissionStep
        assert hasattr(MissionStep, '__table_args__')


# =============================================================================
# TESTS POUR app/models/project.py (sans DB)
# =============================================================================

class TestProjectModel:
    """Tests pour le modèle Project sans DB"""
    
    def test_project_class_exists(self):
        """Tester que la classe Project existe"""
        from app.models.project import Project
        assert Project is not None
    
    def test_project_tablename(self):
        """Tester le nom de la table"""
        from app.models.project import Project
        assert Project.__tablename__ == "projects"
    
    def test_project_has_required_attributes(self):
        """Tester que Project a tous les attributs requis"""
        from app.models.project import Project
        required_attrs = [
            'id', 'project_id', 'name', 'description', 'location',
            'budget', 'status', 'start_date', 'end_date',
            'created_at', 'updated_at', 'extra_metadata'
        ]
        for attr in required_attrs:
            assert hasattr(Project, attr)
    
    def test_project_has_total_missions_property(self):
        """Tester que Project a la propriété total_missions"""
        from app.models.project import Project
        assert hasattr(Project, 'total_missions')
    
    def test_project_has_missions_relationship(self):
        """Tester que Project a la relation missions"""
        from app.models.project import Project
        assert hasattr(Project, 'missions')


# =============================================================================
# TESTS POUR app/models/vault_core.py (sans DB)
# =============================================================================

class TestVaultDocumentModel:
    """Tests pour le modèle VaultDocument sans DB"""
    
    def test_vault_document_class_exists(self):
        """Tester que la classe VaultDocument existe"""
        from app.models.vault_core import VaultDocument
        assert VaultDocument is not None
    
    def test_vault_document_tablename(self):
        """Tester le nom de la table"""
        from app.models.vault_core import VaultDocument
        assert VaultDocument.__tablename__ == "vault_documents"
    
    def test_vault_document_has_required_attributes(self):
        """Tester que VaultDocument a tous les attributs requis"""
        from app.models.vault_core import VaultDocument
        required_attrs = [
            'id', 'document_id', 'file_name', 'file_path', 'file_type',
            'file_size', 'content_hash', 'embedding', 'extra_metadata',
            'status', 'processed_at', 'created_at'
        ]
        for attr in required_attrs:
            assert hasattr(VaultDocument, attr)
    
    def test_vault_document_has_chunks_relationship(self):
        """Tester que VaultDocument a la relation chunks"""
        from app.models.vault_core import VaultDocument
        assert hasattr(VaultDocument, 'chunks')


class TestDocumentChunkModel:
    """Tests pour le modèle DocumentChunk sans DB"""
    
    def test_document_chunk_class_exists(self):
        """Tester que la classe DocumentChunk existe"""
        from app.models.vault_core import DocumentChunk
        assert DocumentChunk is not None
    
    def test_document_chunk_tablename(self):
        """Tester le nom de la table"""
        from app.models.vault_core import DocumentChunk
        assert DocumentChunk.__tablename__ == "document_chunks"
    
    def test_document_chunk_has_required_attributes(self):
        """Tester que DocumentChunk a tous les attributs requis"""
        from app.models.vault_core import DocumentChunk
        required_attrs = [
            'id', 'document_id', 'chunk_index', 'content',
            'embedding', 'start_page', 'end_page', 'extra_metadata'
        ]
        for attr in required_attrs:
            assert hasattr(DocumentChunk, attr)
    
    def test_document_chunk_has_table_args(self):
        """Tester que DocumentChunk a __table_args__"""
        from app.models.vault_core import DocumentChunk
        assert hasattr(DocumentChunk, '__table_args__')
    
    def test_document_chunk_has_document_relationship(self):
        """Tester que DocumentChunk a la relation document"""
        from app.models.vault_core import DocumentChunk
        assert hasattr(DocumentChunk, 'document')


# =============================================================================
# TESTS POUR app/models/__init__.py
# =============================================================================

class TestModelsInit:
    """Tests pour vérifier que tous les modèles sont importables"""
    
    def test_all_models_importable(self):
        """Tester que tous les modèles peuvent être importés depuis app.models"""
        from app.models import (
            Event, MissionEvent, EventType,
            Mission, MissionStep, MissionStatus, MissionStepStatus,
            Project,
            VaultDocument, DocumentChunk
        )
        
        # Vérifier que les classes existent
        assert Event is not None
        assert MissionEvent is not None
        assert EventType is not None
        assert Mission is not None
        assert MissionStep is not None
        assert MissionStatus is not None
        assert MissionStepStatus is not None
        assert Project is not None
        assert VaultDocument is not None
        assert DocumentChunk is not None
    
    def test_models_package_exists(self):
        """Tester que le package app.models existe"""
        import app.models
        assert app.models is not None
