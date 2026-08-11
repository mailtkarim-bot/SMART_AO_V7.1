#!/usr/bin/env python3
"""
Script de génération automatique de tests basiques pour les modules Python.

Ce script parcourt les modules spécifiés et génère des tests unitaires basiques
pour toutes les classes et fonctions trouvés, en se concentrant sur :
- Les dataclasses (test de création, to_dict, etc.)
- Les enums (test des valeurs)
- Les classes avec méthodes statiques
- Les fonctions simples

Utilisation:
    python generate_basic_tests.py --module app.engines.math_engine.zan_solver
"""

import ast
import inspect
import importlib
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


def extract_classes_and_functions(module_path: str) -> Dict[str, List[str]]:
    """
    Extraire les classes et fonctions d'un module.
    
    Args:
        module_path: Chemin du module (ex: "app.engines.math_engine.zan_solver")
    
    Returns:
        Dict avec {"classes": [...], "functions": [...], "enums": [...], "dataclasses": [...]}
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"Erreur: Impossible d'importer {module_path}: {e}")
        return {"classes": [], "functions": [], "enums": [], "dataclasses": []}
    
    classes = []
    functions = []
    enums = []
    dataclasses = []
    
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            # Vérifier si c'est une enum
            if hasattr(obj, "__members__"):
                enums.append(name)
            # Vérifier si c'est une dataclass
            elif hasattr(obj, "__dataclass_fields__"):
                dataclasses.append(name)
            else:
                classes.append(name)
        elif inspect.isfunction(obj) and obj.__module__ == module_path:
            functions.append(name)
    
    return {
        "classes": classes,
        "functions": functions,
        "enums": enums,
        "dataclasses": dataclasses
    }


def generate_test_for_enum(module_path: str, enum_name: str) -> str:
    """Générer des tests pour une enum."""
    test_code = f"""
class Test{enum_name}:
    def test_enum_values(self):
        from {module_path} import {enum_name}
        # Tester que les valeurs de l'enum sont accessibles
        for member in {enum_name}:
            assert hasattr({enum_name}, member.name)
            assert {enum_name}.{member.name}.value == member.value
"""
    return test_code


def generate_test_for_dataclass(module_path: str, class_name: str) -> str:
    """Générer des tests pour une dataclass."""
    test_code = f"""
class Test{class_name}:
    def test_creation(self):
        from {module_path} import {class_name}
        # Tester la création avec des valeurs par défaut
        obj = {class_name}()
        assert obj is not None
    
    def test_creation_with_params(self):
        from {module_path} import {class_name}
        # Tester la création avec des paramètres (à personnaliser)
        # Cette méthode peut échouer si la dataclass a des champs requis
        try:
            obj = {class_name}(**{{}})
            assert obj is not None
        except TypeError:
            # La dataclass a des champs requis, passer
            pass
"""
    return test_code


def generate_test_for_class(module_path: str, class_name: str) -> str:
    """Générer des tests pour une classe."""
    test_code = f"""
class Test{class_name}:
    def test_creation(self):
        from {module_path} import {class_name}
        # Tester la création
        try:
            obj = {class_name}()
            assert obj is not None
        except TypeError as e:
            # La classe a des paramètres requis
            # Essayer avec None ou des valeurs par défaut
            pass
"""
    return test_code


def generate_test_for_function(module_path: str, func_name: str) -> str:
    """Générer des tests pour une fonction."""
    test_code = f"""
class Test{func_name}:
    def test_function_exists(self):
        from {module_path} import {func_name}
        assert callable({func_name})
    
    def test_function_call(self):
        from {module_path} import {func_name}
        # Essayer d'appeler la fonction sans arguments
        try:
            result = {func_name}()
            # Si ça ne lève pas d'erreur, vérifier que le résultat existe
            assert result is not None
        except (TypeError, ValueError):
            # La fonction nécessite des arguments, passer
            pass
"""
    return test_code


def generate_test_file(module_path: str) -> str:
    """
    Générer un fichier de test complet pour un module.
    
    Args:
        module_path: Chemin du module
    
    Returns:
        Code du fichier de test
    """
    components = extract_classes_and_functions(module_path)
    
    imports = f"""\
import pytest
"""
    
    tests = imports
    
    # Générer des tests pour les enums
    for enum_name in components["enums"]:
        tests += generate_test_for_enum(module_path, enum_name)
    
    # Générer des tests pour les dataclasses
    for class_name in components["dataclasses"]:
        tests += generate_test_for_dataclass(module_path, class_name)
    
    # Générer des tests pour les classes
    for class_name in components["classes"]:
        tests += generate_test_for_class(module_path, class_name)
    
    # Générer des tests pour les fonctions
    for func_name in components["functions"]:
        tests += generate_test_for_function(module_path, func_name)
    
    return tests


def main():
    parser = argparse.ArgumentParser(description="Générer des tests unitaires basiques")
    parser.add_argument("--module", required=True, help="Chemin du module (ex: app.engines.math_engine.zan_solver)")
    parser.add_argument("--output", help="Fichier de sortie (par défaut: tests/unit/test_<module>.py)")
    parser.add_argument("--overwrite", action="store_true", help="Écraser le fichier existant")
    
    args = parser.parse_args()
    
    # Générer le fichier de test
    test_code = generate_test_file(args.module)
    
    # Déterminer le fichier de sortie
    if args.output:
        output_file = Path(args.output)
    else:
        # Convertir le chemin du module en nom de fichier de test
        module_parts = args.module.replace(".", "_").replace("app_", "")
        output_file = Path(f"tests/unit/test_{module_parts}.py")
    
    # Vérifier si le fichier existe
    if output_file.exists() and not args.overwrite:
        print(f"Erreur: {output_file} existe déjà. Utilisez --overwrite pour écraser.")
        sys.exit(1)
    
    # Écrire le fichier
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(test_code)
    
    print(f"Tests générés pour {args.module} dans {output_file}")
    print(f"  - Enums: {len(extract_classes_and_functions(args.module)['enums'])}")
    print(f"  - Dataclasses: {len(extract_classes_and_functions(args.module)['dataclasses'])}")
    print(f"  - Classes: {len(extract_classes_and_functions(args.module)['classes'])}")
    print(f"  - Fonctions: {len(extract_classes_and_functions(args.module)['functions'])}")


if __name__ == "__main__":
    main()
