"""
SMART_AO V7 - test_math_engine_no_llm_import.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Test ZERO LLM Import (Gate Bloquant Build 4)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

FORBIDDEN = ['openai', 'anthropic', 'langchain', 'mistralai', 'cohere', 'groq']
ALLOWED = ['sentence_transformers']

def test_scan_math_engine():
    math_dir = project_root / "app" / "engines" / "math_engine"
    py_files = list(math_dir.rglob("*.py"))
    
    forbidden_found = []
    for f in py_files:
        content = f.read_text(errors='ignore')
        for forb in FORBIDDEN:
            # Rechercher uniquement dans les lignes qui sont des imports
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    # Vérifier que le mot interdit est un module complet, pas une sous-chaîne
                    # Exemple: "cohere" doit matcher "import cohere" mais pas "incoherence_detector"
                    import re
                    pattern = r'\b' + re.escape(forb) + r'\b'
                    if re.search(pattern, line) and forb not in ALLOWED:
                        forbidden_found.append(f"{f.relative_to(project_root)}: {line}")
    
    if forbidden_found:
        raise AssertionError(f"LLM imports détectés:\n" + "\n".join(forbidden_found))
    print("✅ Aucun import LLM détecté")

if __name__ == "__main__":
    test_scan_math_engine()
    print("✅ TEST PASSED: Math Engine est ZERO LLM")
