"""
SMART_AO V7 - setup.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from setuptools import setup, find_packages

setup(
    name="smart_ao_v7",
    version="0.1.0",
    description="SMART_AO V7 Engine OS - Système d'exploitation pour AO BTP",
    author="Noor",
    author_email="noor@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "asyncpg>=0.29.0",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "pymupdf>=1.23.0",
        "pdfplumber>=0.10.0",
        "pulp>=2.8.0",
        "ortools>=9.9.0",
        # API & Web (V7)
        "fastapi>=0.120.0",
        "sqlalchemy>=2.0.25",
        "uvicorn>=0.27.0",
        "python-multipart>=0.0.6",
        "streamlit>=1.30.0",
        # Knowledge Engine (V7)
        "qdrant-client>=1.8.0",
        "sentence-transformers>=2.5.0",
        # Security & Auth (V7)
        "pyjwt>=2.8.0",
        "argon2-cffi>=23.1.0",
        # Database migrations
        "alembic>=1.13.0",
        # OCR (V7) - Optional (heavy dependencies)
        # "docling[all]>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
        ],
    },
)
