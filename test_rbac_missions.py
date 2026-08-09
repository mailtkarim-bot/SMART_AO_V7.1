"""Test rapide du filtrage RBAC dans missions.py"""
import sys
sys.path.insert(0, '/workspace')

# Mock des dépendances externes
import unittest.mock as mock

# Mock de la base de données et des settings
with mock.patch.dict('os.environ', {
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'test',
    'DB_USER': 'test',
    'DB_PASSWORD': 'test',
    'SECRET_KEY': 'test_secret_key_for_testing_only_12345678901234567890123456789012',
    'JWT_SECRET': 'test_jwt_secret_for_testing_only_12345678901234567890123456789012',
}):
    # Mock de SQLAlchemy pour éviter la connexion DB
    with mock.patch('app.core.database.create_async_engine'):
        with mock.patch('app.core.database.sessionmaker'):
            # Importer le module après le mock
            from app.api.v1.endpoints.missions import list_missions, get_mission
            from app.engines.security_engine.rbac import get_rbac_enforcer
            from app.models.user import Role
            
            # Vérifier que les imports sont corrects
            enforcer = get_rbac_enforcer()
            
            # Test de filtrage avec des données factices
            test_data = {
                "marge": 15.5,
                "coefficient": 1.85,
                "prix_ht": 100000,
                "nom": "Mission Test",
                "financial_data": {
                    "marge_brute": 15500,
                    "taux_marge": 15.5
                }
            }
            
            # Test avec role PATRON (doit tout voir)
            patron_role = Role.PATRON
            filtered_patron = enforcer.filter_mission_data_by_role(test_data.copy(), patron_role)
            print(f"PATRON - Données filtrées: {filtered_patron}")
            assert "marge" in filtered_patron, "PATRON devrait voir 'marge'"
            assert "financial_data" in filtered_patron, "PATRON devrait voir 'financial_data'"
            
            # Test avec role CONDUCTEUR_TRAVAUX (ne devrait pas voir les données financières)
            conducteur_role = Role.CONDUCTEUR_TRAVAUX
            filtered_conducteur = enforcer.filter_mission_data_by_role(test_data.copy(), conducteur_role)
            print(f"CONDUCTEUR_TRAVAUX - Données filtrées: {filtered_conducteur}")
            assert "marge" not in filtered_conducteur, "CONDUCTEUR_TRAVAUX ne devrait pas voir 'marge'"
            assert "financial_data" not in filtered_conducteur, "CONDUCTEUR_TRAVAUX ne devrait pas voir 'financial_data'"
            assert "nom" in filtered_conducteur, "CONDUCTEUR_TRAVAUX devrait voir 'nom'"
            
            print("\n✅ TOUS LES TESTS RBAC PASSENT - Le filtrage fonctionne correctement")
