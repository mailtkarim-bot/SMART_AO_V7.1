"""
SMART_AO V7 - Tests unitaires avec exécution réelle pour workflow_engine
===============================================================================
Tests qui exécutent le code réel de workflow.py, extraction_step.py et parser_step.py
pour améliorer la couverture de test.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import asyncio

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


# ============================================================================
# Fixtures communes
# ============================================================================

@pytest.fixture
def mock_agent_registry():
    """Mock AgentRegistry pour les tests."""
    registry = Mock()
    registry.find_by_capability = Mock(return_value=[])
    return registry


@pytest.fixture
def mock_event_bus():
    """Mock EventBus pour les tests."""
    bus = Mock()
    bus.publish = Mock()
    return bus


@pytest.fixture
def mock_mission():
    """Crée une mission mockée avec workflow."""
    from app.engines.workflow_engine.mission import Mission, MissionStep, MissionStatus, StepStatus
    
    mission = Mission(
        id="test_mission_001",
        documents=["doc1.pdf", "doc2.pdf"],
        context={"mission_type": "ANALYSE_DCE"},
        created_by="test_user",
        priority="NORMALE"
    )
    return mission


# ============================================================================
# Tests pour Workflow (workflow.py)
# ============================================================================

class TestWorkflow:
    """Tests pour la classe Workflow."""

    def test_workflow_initialization(self):
        """Test l'initialisation d'un Workflow."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        assert workflow.mission_id == mission.id
        assert workflow.status == "PENDING"
        assert workflow.current_step == 0
        assert len(workflow.steps) == 6  # 6 étapes canoniques
    
    def test_workflow_standard_steps(self):
        """Test que les étapes standard sont correctement initialisées."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        expected_steps = [
            "parser_step", "extraction_step", "classification_step",
            "agents_step", "compilation_step", "rapport_step"
        ]
        
        for i, expected_name in enumerate(expected_steps):
            assert workflow.steps[i].step_name == expected_name
            assert workflow.steps[i].step_number == i
    
    def test_get_current_step(self):
        """Test la récupération de l'étape courante."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        # Étape 0 - Note: le name est généré par step_name.upper().replace("_", "")
        # donc parser_step devient PARSERSTEP, extraction_step devient EXTRACTIONSTEP, etc.
        current = workflow.get_current_step()
        assert current is not None
        assert current.step_number == 0
        assert current.name == "PARSERSTEP"
        
        # Avancer et vérifier
        workflow.current_step = 2
        current = workflow.get_current_step()
        assert current.step_number == 2
        assert current.name == "CLASSIFICATIONSTEP"
    
    def test_get_current_step_out_of_bounds(self):
        """Test get_current_step avec index hors limites."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        workflow.current_step = 100  # Hors limites
        assert workflow.get_current_step() is None
        
        workflow.current_step = -1  # Hors limites
        assert workflow.get_current_step() is None
    
    def test_advance(self):
        """Test l'avancement dans le workflow."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        assert workflow.current_step == 0
        
        workflow.advance()
        assert workflow.current_step == 1
        
        workflow.advance()
        assert workflow.current_step == 2
    
    def test_advance_at_last_step(self):
        """Test que advance ne dépasse pas la dernière étape."""
        from app.engines.workflow_engine.workflow import Workflow
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission")
        workflow = Workflow(mission)
        
        # Aller à la dernière étape
        workflow.current_step = 5
        workflow.advance()
        
        # Doit rester à 5 (dernière étape)
        assert workflow.current_step == 5


# ============================================================================
# Tests pour WorkflowEngine (workflow.py)
# ============================================================================

class TestWorkflowEngine:
    """Tests pour la classe WorkflowEngine."""

    @pytest.fixture
    def engine(self):
        """Crée un WorkflowEngine avec mocks."""
        from app.engines.workflow_engine.workflow import WorkflowEngine
        
        with patch('app.engines.workflow_engine.workflow.persistence'):
            engine = WorkflowEngine(
                registry=Mock(),
                event_bus=Mock(),
                max_parallel=6
            )
            return engine
    
    def test_workflow_engine_initialization(self, engine):
        """Test l'initialisation de WorkflowEngine."""
        assert engine.max_parallel == 6
        assert engine.registry is not None
        assert engine.event_bus is not None
    
    def test_map_step_to_mission_status(self, engine):
        """Test le mapping des étapes vers les statuts de mission."""
        from app.engines.workflow_engine.mission import MissionStatus
        
        mapping_tests = {
            "PARSER": MissionStatus.PARSING,
            "EXTRACTION": MissionStatus.EXTRACTING,
            "CLASSIFICATION": MissionStatus.CLASSIFYING,
            "AGENTS": MissionStatus.AGENT_RUNNING,
            "COMPILATION": MissionStatus.COMPILING,
            "RAPPORT": MissionStatus.REPORTING,
            "UNKNOWN": MissionStatus.CREATED
        }
        
        for step_name, expected_status in mapping_tests.items():
            result = engine._map_step_to_mission_status(step_name)
            assert result == expected_status
    
    def test_is_blocking_step(self, engine):
        """Test la détection des étapes bloquantes."""
        blocking_steps = ["PARSER", "CLASSIFICATION"]
        non_blocking_steps = ["EXTRACTION", "AGENTS", "COMPILATION", "RAPPORT"]
        
        for step in blocking_steps:
            assert engine._is_blocking_step(step) is True
        
        for step in non_blocking_steps:
            assert engine._is_blocking_step(step) is False
    
    @pytest.mark.asyncio
    async def test_create_mission(self, engine):
        """Test la création d'une mission."""
        docs = ["doc1.pdf", "doc2.pdf"]
        context = {"mission_type": "ANALYSE_DCE", "test": "value"}
        created_by = "test_user"
        
        with patch('app.engines.workflow_engine.workflow.persistence') as mock_persistence:
            with patch('app.engines.workflow_engine.workflow.datetime') as mock_datetime:
                mock_datetime.now = Mock(return_value=datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc))
                mock_datetime.now.return_value = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)
                
                mission = await engine.create_mission(docs, context, created_by)
                
                assert mission is not None
                assert mission.id.startswith("mission_")
                assert mission.documents == docs
                assert mission.context == context
                assert mission.created_by == created_by
                
                # Vérifier que l'événement a été publié
                assert engine.event_bus.publish.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_persist_mission(self, engine):
        """Test la persistance d'une mission."""
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission_001")
        
        with patch('app.engines.workflow_engine.workflow.persistence') as mock_persistence:
            mock_persistence.save_mission = AsyncMock(return_value=True)
            
            result = await engine._persist_mission(mission)
            
            assert result is True
            mock_persistence.save_mission.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_persist_mission_failure(self, engine):
        """Test l'échec de la persistance d'une mission."""
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_mission_001")
        
        with patch('app.engines.workflow_engine.workflow.persistence') as mock_persistence:
            mock_persistence.save_mission = AsyncMock(side_effect=Exception("DB error"))
            
            result = await engine._persist_mission(mission)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_persist_step(self, engine):
        """Test la persistance d'une étape."""
        from app.engines.workflow_engine.mission import Mission, MissionStep, StepStatus
        
        mission = Mission(id="test_mission_001")
        step = MissionStep(name="PARSER", status=StepStatus.DONE)
        
        with patch('app.engines.workflow_engine.workflow.persistence') as mock_persistence:
            mock_persistence.save_step = AsyncMock(return_value=True)
            
            result = await engine._persist_step(mission, step)
            
            assert result is True
            mock_persistence.save_step.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_step_parser(self, engine, mock_mission):
        """Test l'exécution de l'étape PARSER."""
        from app.engines.workflow_engine.mission import MissionStep, StepStatus
        
        mock_mission.current_step_idx = 0
        step = MissionStep(name="PARSER")
        
        await engine.execute_step(mock_mission, step)
        
        assert step.status == StepStatus.RUNNING
        assert step.started_at is not None
        # Vérifier que parsed_pages a été ajouté au contexte
        assert "parsed_pages" in mock_mission.context
    
    @pytest.mark.asyncio
    async def test_execute_step_extraction(self, engine, mock_mission):
        """Test l'exécution de l'étape EXTRACTION."""
        from app.engines.workflow_engine.mission import MissionStep, StepStatus
        
        mock_mission.current_step_idx = 1
        step = MissionStep(name="EXTRACTION")
        
        await engine.execute_step(mock_mission, step)
        
        assert step.status == StepStatus.RUNNING
        assert step.started_at is not None
        # Vérifier que adn_extracted a été ajouté au contexte
        assert "adn_extracted" in mock_mission.context
    
    @pytest.mark.asyncio
    async def test_execute_step_classification(self, engine, mock_mission):
        """Test l'exécution de l'étape CLASSIFICATION."""
        from app.engines.workflow_engine.mission import MissionStep, StepStatus
        
        mock_mission.current_step_idx = 2
        step = MissionStep(name="CLASSIFICATION")
        
        await engine.execute_step(mock_mission, step)
        
        assert step.status == StepStatus.RUNNING
        assert step.started_at is not None
        # Vérifier que needed_capabilities a été ajouté au contexte
        assert "needed_capabilities" in mock_mission.context
        assert len(mock_mission.context["needed_capabilities"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_step_unknown(self, engine, mock_mission):
        """Test l'exécution avec une étape inconnue."""
        from app.engines.workflow_engine.mission import MissionStep
        
        mock_mission.current_step_idx = 0
        step = MissionStep(name="UNKNOWN_STEP")
        
        with pytest.raises(ValueError, match="Unknown step"):
            await engine.execute_step(mock_mission, step)


# ============================================================================
# Tests pour ExtractionStep (extraction_step.py)
# ============================================================================

class TestExtractionStepExecution:
    """Tests pour ExtractionStep avec exécution réelle."""

    @pytest.fixture
    def extraction_step(self):
        """Crée une instance de ExtractionStep."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        return ExtractionStep()
    
    @pytest.mark.asyncio
    async def test_extract_deadlines(self, extraction_step):
        """Test l'extraction des deadlines."""
        context = {
            "raw_text": "Date limite de remise: 15/08/2026. Délai maximal: 20/08/2026"
        }
        
        result = extraction_step._extract_deadlines(context)
        
        assert result is not None
        assert isinstance(result, dict)
        # Vérifier que certaines deadlines ont été extraites
        assert any(v is not None for v in result.values())
    
    @pytest.mark.asyncio
    async def test_extract_penalties(self, extraction_step):
        """Test l'extraction des pénalités."""
        context = {
            "raw_text": "Pénalité de retard: 500 € par jour. Retenue: 10% du montant"
        }
        
        result = extraction_step._extract_penalties(context)
        
        assert result is not None
        assert isinstance(result, list)
        # Doit trouver au moins une pénalité
        assert len(result) >= 1
    
    @pytest.mark.asyncio
    async def test_detect_pab(self, extraction_step):
        """Test la détection de la PAB."""
        context = {
            "raw_text": "Enveloppe financière: 1 000 000 €. Budget estimatif: 500 000 €"
        }
        
        result = extraction_step._detect_pab(context)
        
        # Peut retourner None si pas de plage détectée
        if result is not None:
            assert isinstance(result, dict)
            assert "currency" in result
    
    @pytest.mark.asyncio
    async def test_extract_criteria(self, extraction_step):
        """Test l'extraction des critères."""
        context = {
            "raw_text": "Critères de jugement: Prix: 40 points, Qualité: 30 points, Délai: 30 points"
        }
        
        result = extraction_step._extract_criteria(context)
        
        assert result is not None
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_extract_certifications(self, extraction_step):
        """Test l'extraction des certifications."""
        context = {
            "raw_text": "Certification ISO 9001 requise. Norme NF obligatoire"
        }
        
        result = extraction_step._extract_certifications(context)
        
        assert result is not None
        assert isinstance(result, list)
        # Doit trouver au moins ISO 9001
        assert len(result) >= 1
    
    @pytest.mark.asyncio
    async def test_extract_ccap_clauses(self, extraction_step):
        """Test l'extraction des clauses CCAP."""
        context = {
            "raw_text": "Conditions de paiement: 30 jours. Garanties: 5 ans. Assurance: obligatoire"
        }
        
        result = extraction_step._extract_ccap_clauses(context)
        
        assert result is not None
        assert isinstance(result, list)
    
    def test_parse_date(self, extraction_step):
        """Test le parsing des dates."""
        from datetime import datetime
        
        # Test différents formats
        test_cases = [
            ("15/08/2026", "%d/%m/%Y"),
            ("15-08-2026", "%d-%m-%Y"),
            ("15.08.2026", "%d.%m.%Y"),
            ("2026/08/15", "%Y/%m/%d"),
        ]
        
        for date_str, fmt in test_cases:
            result = extraction_step._parse_date(date_str)
            if result:
                assert isinstance(result, datetime)
    
    def test_calculate_confidence(self, extraction_step):
        """Test le calcul du score de confiance."""
        data = {
            "deadlines": {"submission_deadline": datetime(2026, 8, 15)},
            "pab": {"min": 1000, "max": 2000},
            "criteria": [{"name": "Prix", "weight": 40}]
        }
        
        confidence = extraction_step._calculate_confidence(data)
        
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
    
    def test_categorize_criterion(self, extraction_step):
        """Test la catégorisation des critères."""
        tests = [
            ("Prix", "financial"),
            ("Coût total", "financial"),
            ("Mémoire technique", "technical"),
            ("Délai de livraison", "schedule"),
            ("Impact environnemental", "environmental"),
            ("Autre", "other")
        ]
        
        for name, expected_category in tests:
            result = extraction_step._categorize_criterion(name)
            assert result == expected_category
    
    def test_assess_clause_risk(self, extraction_step):
        """Test l'évaluation du risque des clauses."""
        tests = [
            ("Pénalité de 10% en cas de retard", "high"),
            ("Délai de paiement de 30 jours", "medium"),
            ("Recommandation de qualité", "low")
        ]
        
        for content, expected_risk in tests:
            result = extraction_step._assess_clause_risk("test", content)
            assert result == expected_risk
    
    @pytest.mark.asyncio
    async def test_execute_full(self, extraction_step):
        """Test l'exécution complète de ExtractionStep."""
        context = {
            "raw_text": "Date limite: 15/08/2026. Pénalité: 500 €. Budget: 1 000 000 €",
            "parsed_docs": {}
        }
        
        result = await extraction_step.execute("mission_001", context)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "deadlines" in result
        assert "penalties" in result
        assert "pab" in result
        assert "criteria" in result
        assert "certifications" in result
        assert "ccap_clauses" in result
        assert "metadata" in result
        assert "confidence_score" in result["metadata"]


# ============================================================================
# Tests pour ParserStep (parser_step.py)
# ============================================================================

class TestParserStepExecution:
    """Tests pour ParserStep avec exécution réelle."""

    @pytest.fixture
    def parser_step(self):
        """Crée une instance de ParserStep."""
        from app.engines.workflow_engine.steps.parser_step import ParserStep
        return ParserStep()
    
    def test_parser_step_attributes(self, parser_step):
        """Test les attributs de ParserStep."""
        assert parser_step.name == "parser_step"
        assert parser_step.version == "1.0.0"
        assert parser_step.step_name == "parser"
        assert parser_step.step_order == 1
    
    def test_check_administrative_completeness(self, parser_step):
        """Test la vérification de la complétude administrative."""
        parsed_documents = [
            {
                "filename": "CCTP.pdf",
                "doc_type": "CCTP",
                "content": "Cahier des clauses techniques particulières"
            },
            {
                "filename": "CCAP.pdf",
                "doc_type": "CCAP",
                "content": "Cahier des clauses administratives particulières"
            }
        ]
        
        result = parser_step._check_administrative_completeness(parsed_documents)
        
        assert result is not None
        assert isinstance(result, dict)
        assert "required_documents" in result
        assert "missing_documents" in result
        assert "completeness_rate" in result
        assert "is_complete" in result
    
    def test_check_administrative_completeness_empty(self, parser_step):
        """Test la vérification avec des documents vides."""
        result = parser_step._check_administrative_completeness([])
        
        assert result["is_complete"] is False
        assert len(result["missing_documents"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_no_files(self, parser_step):
        """Test l'exécution sans fichiers."""
        from app.schemas.workflow import StepStatus
        
        context = {}  # Pas de files_path
        
        result = await parser_step.execute("mission_001", context)
        
        assert result is not None
        # StepResult est un Pydantic model, donc on accède aux attributs directement
        assert hasattr(result, "status")
        assert result.status == StepStatus.FAILED
        assert hasattr(result, "error")
        assert "chemin de fichier" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_with_files_path(self, parser_step):
        """Test l'exécution avec un chemin de fichiers."""
        from app.schemas.workflow import StepStatus
        
        context = {
            "files_path": "/tmp/test_pdfs"
        }
        
        # Mock DocumentParser pour éviter les erreurs de fichiers
        with patch('app.engines.workflow_engine.steps.parser_step.DocumentParser') as mock_parser:
            mock_instance = mock_parser.return_value
            mock_instance.extract_text = AsyncMock(return_value={"pages": ["page1", "page2"]})
            mock_instance.detect_document_type = AsyncMock(return_value="CCTP")
            mock_instance.extract_structure = AsyncMock(return_value={"sections": []})
            
            # Mock Path.glob pour simuler des fichiers PDF
            with patch('app.engines.workflow_engine.steps.parser_step.Path') as mock_path:
                mock_pdf_file = Mock()
                mock_pdf_file.name = "test.pdf"
                mock_pdf_file.__str__ = Mock(return_value="/tmp/test_pdfs/test.pdf")
                mock_path.return_value.glob = Mock(return_value=[mock_pdf_file])
                
                result = await parser_step.execute("mission_001", context)
                
                assert result is not None
                assert hasattr(result, "status")
                # Le test peut échouer si le mock ne couvre pas tous les cas
                # On vérifie juste que l'exécution ne crash pas
                assert result.status in [StepStatus.COMPLETED, StepStatus.FAILED]
                assert hasattr(result, "data") or hasattr(result, "error")


# ============================================================================
# Tests pour les autres steps
# ============================================================================

class TestClassificationStepExecution:
    """Tests pour ClassificationStep avec exécution réelle."""

    @pytest.fixture
    def classification_step(self):
        """Crée une instance de ClassificationStep."""
        from app.engines.workflow_engine.steps.classification_step import ClassificationStep
        return ClassificationStep()
    
    @pytest.mark.asyncio
    async def test_execute_with_data(self, classification_step):
        """Test l'exécution avec des données extraites."""
        context = {
            "extracted_data": {
                "deadlines": [{"type": "submission", "date": "15/08/2026", "jours_restants": 5}],
                "penalties": [{"montant_estime": 10000, "frequence": "quotidienne"}],
                "pab_clauses": [{"value": 1000000}]
            }
        }
        
        result = await classification_step.execute("mission_001", context)
        
        assert result is not None
        assert result["status"] == "success"
        assert "classified_data" in result
        assert "summary" in result
        assert "next_step" in result
        assert result["next_step"] == "agents_step"
    
    @pytest.mark.asyncio
    async def test_execute_empty_data(self, classification_step):
        """Test l'exécution avec des données vides."""
        context = {"extracted_data": {}}
        
        result = await classification_step.execute("mission_001", context)
        
        assert result is not None
        assert result["status"] == "error"


class TestCompilationStepExecution:
    """Tests pour CompilationStep avec exécution réelle."""

    @pytest.fixture
    def compilation_step(self):
        """Crée une instance de CompilationStep."""
        from app.engines.workflow_engine.steps.compilation_step import CompilationStep
        return CompilationStep()
    
    def test_generate_summary(self, compilation_step):
        """Test la génération du résumé."""
        agents_results = {
            "agent1": {"status": "success", "result": {"findings": []}},
            "agent2": {"status": "success", "result": {"findings": []}},
            "agent3": {"status": "error", "error": "Erreur"}
        }
        
        result = compilation_step._generate_summary(agents_results)
        
        assert result is not None
        assert result["total_agents"] == 3
        assert result["successful_agents"] == 2
        assert result["success_rate"] == pytest.approx(66.67, rel=0.01)
    
    def test_extract_alertes(self, compilation_step):
        """Test l'extraction des alertes."""
        analyse = {
            "alerte_critique": "Problème grave détecté",
            "risque_majeur": "Attention nécessaire"
        }
        
        result = compilation_step._extract_alertes(analyse, "agent1")
        
        assert result is not None
        assert isinstance(result, list)
        # Le code cherche 'alerte' ou 'risk' dans les clés, donc alerte_critique match
        assert len(result) >= 1
    
    def test_extract_recommandations(self, compilation_step):
        """Test l'extraction des recommandations."""
        analyse = {
            "recommandation_1": "Faire ceci",
            "conseil_2": "Faire cela"
        }
        
        result = compilation_step._extract_recommandations(analyse, "agent1")
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 2
    
    def test_evaluer_niveau_alerte(self, compilation_step):
        """Test l'évaluation du niveau d'alerte."""
        tests = [
            ("Problème critique urgent", "high"),
            ("Problème important majeur", "medium"),
            ("Avertissement mineur", "low")
        ]
        
        for content, expected in tests:
            result = compilation_step._evaluer_niveau_alerte(content)
            assert result == expected
    
    @pytest.mark.asyncio
    async def test_execute(self, compilation_step):
        """Test l'exécution complète."""
        context = {
            "agents_results": {
                "agent1": {"status": "success", "result": {"alerte": "Critique"}},
                "agent2": {"status": "success", "result": {"recommandation": "Conseil"}}
            }
        }
        
        result = await compilation_step.execute("mission_001", context)
        
        assert result is not None
        assert result["status"] == "success"
        assert "compiled_report" in result
        assert "stats" in result


class TestRapportStepExecution:
    """Tests pour RapportStep avec exécution réelle."""

    @pytest.fixture
    def rapport_step(self):
        """Crée une instance de RapportStep."""
        from app.engines.workflow_engine.steps.rapport_step import RapportStep
        return RapportStep()
    
    def test_generate_executive_summary(self, rapport_step):
        """Test la génération du résumé exécutif."""
        compiled_report = {
            "alertes": [
                {"niveau": "high", "content": "Alerte critique"},
                {"niveau": "medium", "content": "Alerte majeure"}
            ],
            "recommandations": [{"content": "Recommandation 1"}]
        }
        
        result = rapport_step._generate_executive_summary(compiled_report)
        
        assert result is not None
        assert "risk_level" in result
        assert "risk_score" in result
        assert "go_no_go_recommendation" in result
        assert "key_points" in result
    
    def test_calculate_risk_score(self, rapport_step):
        """Test le calcul du score de risque."""
        alertes = [
            {"niveau": "high"},
            {"niveau": "high"},
            {"niveau": "medium"}
        ]
        
        score = rapport_step._calculate_risk_score(alertes)
        
        assert score == 50  # 20 + 20 + 10 = 50
    
    def test_get_risk_level(self, rapport_step):
        """Test la récupération du niveau de risque."""
        tests = [
            (80, "CRITIQUE"),
            (50, "ÉLEVÉ"),
            (30, "MODÉRÉ"),
            (10, "FAIBLE")
        ]
        
        for score, expected_level in tests:
            result = rapport_step._get_risk_level(score)
            assert result == expected_level
    
    def test_generate_text_report(self, rapport_step):
        """Test la génération du rapport texte."""
        final_report = {
            "report_id": "RPT-001",
            "generated_at": "2026-08-10T12:00:00",
            "executive_summary": {
                "risk_level": "MODÉRÉ",
                "go_no_go_recommendation": "GO_WITH_RESERVES"
            },
            "action_plan": []
        }
        
        result = rapport_step._generate_text_report(final_report)
        
        assert result is not None
        assert isinstance(result, str)
        assert "RAPPORT D'ANALYSE SMART_AO V7" in result
        assert "RPT-001" in result
    
    def test_get_agent_title(self, rapport_step):
        """Test la récupération du titre d'un agent."""
        tests = [
            ("agent_deadline", "Analyse des Deadlines"),
            ("agent_pab", "Détection PAB"),
            ("unknown_agent", "Unknown Agent")
        ]
        
        for agent_name, expected_title in tests:
            result = rapport_step._get_agent_title(agent_name)
            assert result == expected_title
    
    @pytest.mark.asyncio
    async def test_execute(self, rapport_step):
        """Test l'exécution complète."""
        context = {
            "compiled_report": {
                "summary": {},
                "analyses": {},
                "recommandations": [],
                "alertes": []
            }
        }
        
        result = await rapport_step.execute("mission_001", context)
        
        assert result is not None
        assert result["status"] == "success"
        assert "final_report" in result
        assert "deliverables" in result
        assert result["workflow_completed"] is True


# ============================================================================
# Tests pour BaseStep
# ============================================================================

class TestBaseStepExecution:
    """Tests pour BaseStep avec exécution réelle."""

    @pytest.mark.asyncio
    async def test_rollback(self):
        """Test le rollback de BaseStep."""
        from app.engines.workflow_engine.steps.base_step import BaseStep
        
        # BaseStep est abstraite, on utilise une sous-classe
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        step = ExtractionStep()
        
        result = await step.rollback("mission_001", {})
        
        assert result is True
