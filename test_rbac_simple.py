"""Test simple du filtrage RBAC"""
import sys
sys.path.insert(0, '/workspace')

from app.engines.security_engine.rbac import get_rbac_enforcer
from app.models.user import Role

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
print(f"PATRON - Données filtrées: {list(filtered_patron.keys())}")
assert "marge" in filtered_patron, "PATRON devrait voir 'marge'"
assert "financial_data" in filtered_patron, "PATRON devrait voir 'financial_data'"

# Test avec role CONDUCTEUR_TRAVAUX (ne devrait pas voir les données financières)
conducteur_role = Role.CONDUCTEUR_TRAVAUX
filtered_conducteur = enforcer.filter_mission_data_by_role(test_data.copy(), conducteur_role)
print(f"CONDUCTEUR_TRAVAUX - Données filtrées: {list(filtered_conducteur.keys())}")
assert "marge" not in filtered_conducteur, "CONDUCTEUR_TRAVAUX ne devrait pas voir 'marge'"
assert "financial_data" not in filtered_conducteur, "CONDUCTEUR_TRAVAUX ne devrait pas voir 'financial_data'"
assert "nom" in filtered_conducteur, "CONDUCTEUR_TRAVAUX devrait voir 'nom'"

print("\n✅ TOUS LES TESTS RBAC PASSENT - Le filtrage fonctionne correctement")
