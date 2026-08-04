#!/usr/bin/env python3
"""
SMART_AO V7 - REC-015 Validation: Persistance PostgreSQL
=====================================================
Valide l'implémentation de la persistance PostgreSQL pour REC-015.

Ce script vérifie:
- Les migrations Alembic sont correctement configurées
- Les modèles SQLAlchemy sont importables
- La configuration de la base de données est valide
- Les métadonnées des migrations sont complètes
"""

import sys
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate_migrations():
    """Valider que les migrations Alembic sont correctement configurées"""
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    
    print("🔍 Validation des migrations Alembic...")
    
    try:
        # Vérifier les fichiers de migration dans le dossier versions
        migrations_dir = PROJECT_ROOT / "app" / "alembic" / "versions"
        migration_files = sorted(migrations_dir.glob("*.py"))
        
        expected_migrations = ['0016', '0017', '0018', '0019']
        found_migrations = []
        
        for migration_file in migration_files:
            if migration_file.name.startswith("__"):
                continue
            
            # Extraire l'ID de migration du nom de fichier
            mig_id = migration_file.name.split('_')[0]
            found_migrations.append(mig_id)
            
            # Lire le docstring
            content = migration_file.read_text()
            doc = content.split('"""')[1] if '"""' in content else "No description"
            print(f"  ✅ Migration {mig_id}: {doc.split(chr(10))[0] if doc else 'No description'}")
        
        # Vérifier que toutes les migrations attendues sont présentes
        missing = [m for m in expected_migrations if m not in found_migrations]
        if missing:
            print(f"  ❌ Migrations manquantes: {missing}")
            return False, f"Migrations manquantes: {missing}"
        
        print(f"  ✅ Toutes les migrations trouvées: {len(found_migrations)} migrations")
        return True, f"{len(found_migrations)} migrations validées"
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False, str(e)


def validate_models():
    """Valider que tous les modèles SQLAlchemy sont importables"""
    print("🔍 Validation des modèles SQLAlchemy...")
    
    try:
        # Importer tous les modèles
        from app.models.vault_core import VaultDocument, DocumentChunk
        from app.models.project import Project
        from app.models.mission import Mission, MissionStep, MissionStatus, MissionStepStatus
        from app.models.events import Event, EventType, MissionEvent
        
        models = [
            VaultDocument, DocumentChunk, Project,
            Mission, MissionStep, MissionStatus, MissionStepStatus,
            Event, EventType, MissionEvent
        ]
        
        for model in models:
            print(f"  ✅ Modèle {model.__name__} importé")
            if hasattr(model, '__tablename__'):
                print(f"     Table: {model.__tablename__}")
        
        return True, f"{len(models)} modèles validés"
        
    except Exception as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False, str(e)


def validate_database_config():
    """Valider la configuration de la base de données"""
    print("🔍 Validation de la configuration base de données...")
    
    try:
        from app.core.database import DATABASE_URL, Base, engine
        
        print(f"  ✅ DATABASE_URL configurée")
        print(f"     URL: {DATABASE_URL}")
        print(f"  ✅ Base (SQLAlchemy) disponible")
        print(f"  ✅ Moteur SQLAlchemy async créé")
        
        # Vérifier que les métadonnées contiennent tous les modèles
        table_names = [table.name for table in Base.metadata.tables.values()]
        expected_tables = [
            'vault_documents', 'document_chunks',
            'projects',
            'missions', 'mission_steps', 'mission_events',
            'events'
        ]
        
        for table in expected_tables:
            if table in table_names:
                print(f"  ✅ Table {table} dans métadonnées")
            else:
                print(f"  ❌ Table {table} MANQUANTE dans métadonnées")
                return False, f"Table {table} manquante"
        
        return True, f"{len(table_names)} tables validées"
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False, str(e)


def validate_migration_metadata():
    """Valider les métadonnées des fichiers de migration"""
    print("🔍 Validation des métadonnées des migrations...")
    
    migrations_dir = PROJECT_ROOT / "app" / "alembic" / "versions"
    
    for migration_file in sorted(migrations_dir.glob("*.py")):
        if migration_file.name.startswith("__"):
            continue
        
        # Lire le fichier
        content = migration_file.read_text()
        
        # Vérifier les métadonnées requises
        required = ['revision =', 'down_revision =', 'branch_labels =', 'depends_on =']
        missing = [r for r in required if r not in content]
        
        if missing:
            print(f"  ❌ {migration_file.name}: métadonnées manquantes: {missing}")
            return False, f"{migration_file.name} manquant: {missing}"
        else:
            print(f"  ✅ {migration_file.name}: toutes les métadonnées présentes")
    
    return True, "Toutes les métadonnées validées"


def validate_requirements():
    """Valider que les dépendances nécessaires sont dans requirements.txt"""
    print("🔍 Validation des dépendances PostgreSQL...")
    
    requirements_file = PROJECT_ROOT / "requirements.txt"
    content = requirements_file.read_text()
    
    required_packages = ['alembic', 'psycopg2-binary', 'asyncpg', 'sqlalchemy']
    missing = []
    
    for pkg in required_packages:
        if pkg.lower() in content.lower():
            print(f"  ✅ {pkg} présent dans requirements.txt")
        else:
            print(f"  ❌ {pkg} MANQUANT dans requirements.txt")
            missing.append(pkg)
    
    if missing:
        return False, f"Paquets manquants: {missing}"
    
    return True, "Toutes les dépendances validées"


def validate_setup_py():
    """Valider que setup.py inclut les dépendances PostgreSQL"""
    print("🔍 Validation de setup.py...")
    
    setup_file = PROJECT_ROOT / "setup.py"
    content = setup_file.read_text()
    
    required_packages = ['alembic', 'psycopg2-binary']
    missing = []
    
    for pkg in required_packages:
        if pkg.lower() in content.lower():
            print(f"  ✅ {pkg} présent dans setup.py")
        else:
            print(f"  ❌ {pkg} MANQUANT dans setup.py")
            missing.append(pkg)
    
    if missing:
        return False, f"Paquets manquants: {missing}"
    
    return True, "setup.py validé"


def main():
    """Exécuter toutes les validations REC-015"""
    print("=" * 80)
    print("🚀 SMART_AO V7 - REC-015 Validation: Persistance PostgreSQL")
    print("=" * 80)
    print()
    
    # Liste des validations
    validations = [
        ("Migrations Alembic", validate_migrations),
        ("Modèles SQLAlchemy", validate_models),
        ("Configuration Base de Données", validate_database_config),
        ("Métadonnées des Migrations", validate_migration_metadata),
        ("Dépendances requirements.txt", validate_requirements),
        ("Configuration setup.py", validate_setup_py),
    ]
    
    results = []
    
    for name, validator in validations:
        try:
            passed, message = validator()
            results.append({
                'name': name,
                'passed': passed,
                'message': message
            })
        except Exception as e:
            results.append({
                'name': name,
                'passed': False,
                'message': str(e)
            })
        print()
    
    # Afficher le résumé
    print("=" * 80)
    print("📊 RÉSULTATS REC-015")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} | {result['name']}: {result['message']}")
    
    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Taux de succès: {passed/total*100:.1f}%")
    print("=" * 80)
    
    if failed == 0:
        print("✅ REC-015 VALIDÉE À 100%")
        return 0
    else:
        print(f"❌ REC-015: {failed} validation(s) échouée(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
