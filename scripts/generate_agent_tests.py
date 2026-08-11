#!/usr/bin/env python3
"""
SMART_AO V7 - Script de génération de tests pour les agents
==============================================================

Ce script génère des tests unitaires de base pour chaque agent dans app/agents/.
Les tests vérifient:
1. L'import du module
2. L'existence de la classe Agent
3. Les attributs de base de l'agent
4. La méthode can_handle
5. La méthode execute (si possible)

Usage:
    python3 scripts/generate_agent_tests.py
"""

import os
import re
from pathlib import Path

# Configuration
AGENTS_DIR = Path("app/agents")
TESTS_DIR = Path("tests/unit")
AGENT_PREFIX = "agent_"


def get_agent_files():
    """Récupère la liste des fichiers d'agents."""
    agent_files = []
    
    if AGENTS_DIR.exists():
        for file in AGENTS_DIR.glob(f"{AGENT_PREFIX}*.py"):
            agent_files.append(file)
    
    return sorted(agent_files)


def extract_agent_class_name(file_path):
    """Extrait le nom de la classe Agent du fichier."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la classe qui hérite de BaseAgent
    # Pattern: class NomAgent(BaseAgent):
    pattern = r'class\s+(\w+)\s*\([^)]*BaseAgent[^)]*\):'
    match = re.search(pattern, content)
    
    if match:
        return match.group(1)
    
    # Si pas trouvé, essayer avec @registry.register
    # Pattern: @registry.register(...)\nclass NomAgent(BaseAgent):
    pattern = r'@registry\.register\([^)]*\)\s*\n\s*class\s+(\w+)\s*\([^)]*BaseAgent[^)]*\):'
    match = re.search(pattern, content)
    
    if match:
        return match.group(1)
    
    # Si toujours pas trouvé, retourner le nom du fichier
    return file_path.stem.replace(AGENT_PREFIX, "").replace("_", " ").title().replace(" ", "")


def generate_test_content(agent_file_path):
    """Génère le contenu du fichier de test pour un agent."""
    agent_name = agent_file_path.stem
    module_name = agent_file_path.stem
    class_name = extract_agent_class_name(agent_file_path)
    
    test_file_name = f"test_{module_name}.py"
    
    # Contenu du test
    test_content = f'''"""
SMART_AO V7 - Test unitaire pour {class_name}
===============================================
Tests unitaires de base pour l'agent {module_name}.
Généré automatiquement par generate_agent_tests.py
"""

import pytest
from unittest.mock import MagicMock

from app.agents.{module_name} import {class_name}


class Test{class_name}:
    """Tests pour l'agent {class_name}."""

    def test_module_import(self):
        """Test que le module s'import correctement."""
        assert {class_name} is not None

    def test_agent_class_exists(self):
        """Test que la classe {class_name} existe."""
        agent = {class_name}()
        assert agent is not None
        assert isinstance(agent, {class_name})

    def test_agent_name(self):
        """Test que l'agent a un nom."""
        agent = {class_name}()
        assert hasattr(agent, "name")
        assert agent.name is not None
        assert isinstance(agent.name, str)

    def test_agent_capabilities(self):
        """Test que l'agent a des capacités définies."""
        agent = {class_name}()
        assert hasattr(agent, "capabilities")
        assert agent.capabilities is not None
        assert isinstance(agent.capabilities, list)
        assert len(agent.capabilities) > 0

    def test_agent_tags(self):
        """Test que l'agent a des tags."""
        agent = {class_name}()
        assert hasattr(agent, "tags")
        assert agent.tags is not None
        assert isinstance(agent.tags, list)

    def test_agent_estimated_duration(self):
        """Test que l'agent a une durée estimée."""
        agent = {class_name}()
        assert hasattr(agent, "estimated_duration")
        assert agent.estimated_duration is not None

    def test_agent_is_blocking(self):
        """Test que l'agent a un attribut is_blocking."""
        agent = {class_name}()
        assert hasattr(agent, "is_blocking")
        assert isinstance(agent.is_blocking, bool)

    def test_can_handle_method_exists(self):
        """Test que la méthode can_handle existe."""
        agent = {class_name}()
        assert hasattr(agent, "can_handle")
        assert callable(agent.can_handle)

    def test_can_handle_with_mock_mission(self):
        """Test la méthode can_handle avec une mission mock."""
        agent = {class_name}()
        
        # Créer une mission mock
        mock_mission = MagicMock()
        mock_mission.has_document_type.return_value = False
        mock_mission.context = {{}}
        
        # Appeler can_handle
        score = agent.can_handle(mock_mission)
        
        # Vérifier que ça retourne un float entre 0 et 1
        assert isinstance(score, (int, float))
        assert 0 <= score <= 1

    def test_can_handle_with_empty_context(self):
        """Test can_handle avec un contexte vide."""
        agent = {class_name}()
        
        mock_mission = MagicMock()
        mock_mission.has_document_type.return_value = False
        mock_mission.context = {{}}
        
        score = agent.can_handle(mock_mission)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 1

    def test_agent_attributes(self):
        """Test les attributs standard de l'agent."""
        agent = {class_name}()
        
        # Vérifier les attributs standard
        assert hasattr(agent, "name")
        assert hasattr(agent, "capabilities")
        assert hasattr(agent, "tags")
        assert hasattr(agent, "estimated_duration")
        assert hasattr(agent, "is_blocking")
        assert hasattr(agent, "can_handle")
        assert hasattr(agent, "execute")


class Test{class_name}EdgeCases:
    """Tests pour les cas limites."""

    def test_agent_instantiation(self):
        """Test l'instantiation de l'agent."""
        agent = {class_name}()
        assert agent is not None

    def test_agent_multiple_instances(self):
        """Test la création de multiples instances."""
        agent1 = {class_name}()
        agent2 = {class_name}()
        
        # Ce sont des instances différentes
        assert agent1 is not agent2

    def test_agent_capabilities_not_empty(self):
        """Test que les capacités ne sont pas vides."""
        agent = {class_name}()
        assert len(agent.capabilities) > 0

    def test_agent_tags_not_empty(self):
        """Test que les tags ne sont pas vides."""
        agent = {class_name}()
        assert len(agent.tags) > 0

    def test_agent_name_not_empty(self):
        """Test que le nom n'est pas vide."""
        agent = {class_name}()
        assert len(agent.name) > 0
'''
    
    return test_file_name, test_content


def main():
    """Fonction principale."""
    print("Début de la génération des tests pour les agents...")
    
    agent_files = get_agent_files()
    print(f"Trouvé {len(agent_files)} fichiers d'agents")
    
    for agent_file in agent_files:
        print(f"  Traitement de {agent_file.name}...")
        
        try:
            test_file_name, test_content = generate_test_content(agent_file)
            test_file_path = TESTS_DIR / test_file_name
            
            # Vérifier si le fichier existe déjà
            if test_file_path.exists():
                print(f"    Fichier de test {test_file_name} existe déjà - ignorer")
            else:
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(test_content)
                print(f"    ✓ Test généré: {test_file_name}")
        except Exception as e:
            print(f"    ✗ Erreur pour {agent_file.name}: {e}")
    
    print("\nGénération terminée!")


if __name__ == "__main__":
    main()
