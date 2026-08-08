"""
SMART_AO V7.1 - test_local_llm_fallback.py
============================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Local LLM Fallback (ADR-060)
Source: ARCHITECTURE_V7_ENGINE.md ADR-060
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.knowledge_engine.local_llm import LocalLLMClient
from app.engines.knowledge_engine.confidentialite_detector import detect_confidentialite


def test_detect_confidential_defense():
    text = "Ce DCE est classé CONFIDENTIEL DÉFENSE et concerne un site nucléaire."
    result = detect_confidentialite(text)
    assert result["confidential"] is True
    assert result["recommended_handler"] == "local_llm"
    print(f"✅ Confidentialité détectée: {result['markers']}")


def test_detect_non_confidential():
    text = "Marché public de construction d'un bâtiment administratif."
    result = detect_confidentialite(text)
    assert result["confidential"] is False
    print("✅ DCE standard non confidentiel")


def test_local_llm_fallback_response():
    async def run():
        client = LocalLLMClient()
        response = await client.generate(
            "Résume ce DCE confidentiel.",
            context={"confidential": True},
            force_local=True,
        )
        assert response.local is True
        assert response.confidential is True
        assert response.fallback is True  # Ollama non disponible en test
        assert "FALLBACK LOCAL" in response.text
        assert "[CONFIDENTIEL]" in response.text
        print("✅ Fallback local actif pour DCE confidentiel")

    asyncio.run(run())


def test_local_llm_analyze_dce():
    async def run():
        client = LocalLLMClient()
        response = await client.analyze_dce(
            "DCE CONFIDENTIEL DÉFENSE. Construction hangar militaire."
        )
        assert response.confidential is True
        assert response.local is True
        print("✅ Analyse DCE confidentiel en local")

    asyncio.run(run())


if __name__ == "__main__":
    test_detect_confidential_defense()
    test_detect_non_confidential()
    test_local_llm_fallback_response()
    test_local_llm_analyze_dce()
    print("✅ TESTS PASSED: Local LLM Fallback")
