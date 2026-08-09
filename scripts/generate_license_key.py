#!/usr/bin/env python3
"""
SMART_AO V7 - License Key Generator
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Générateur de clés de licence pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §5.1

Ce script génère des clés de licence pour les installations SMART_AO V7.
Format des clés: XXXX-XXXX-XXXX-XXXX (16 caractères alphanumériques)
"""

import argparse
import json
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path


class LicenseGenerator:
    """Générateur de clés de licence."""
    
    def __init__(self):
        self.license_database = Path("licenses.json")
        
    def generate_license_key(self, length: int = 16) -> str:
        """Générer une clé de licence aléatoire."""
        alphabet = string.ascii_uppercase + string.digits
        key = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Formater en groups de 4 caractères
        return '-'.join([key[i:i+4] for i in range(0, length, 4)])
    
    def generate_hash(self, customer_info: str, salt: str) -> str:
        """Générer un hash pour la validation."""
        data = f"{customer_info}{salt}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def create_license(
        self,
        customer_name: str,
        customer_email: str,
        product: str = "SMART_AO_V7",
        license_type: str = "standard",
        max_users: int = 10,
        expires_in_days: Optional[int] = 365,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Créer une nouvelle licence complète."""
        # Générer une clé unique
        license_key = self.generate_license_key()
        
        # Générer un salt
        salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # Calculer le hash de validation
        validation_hash = self.generate_hash(customer_email, salt)
        
        # Calculer la date d'expiration
        expiration_date = None
        if expires_in_days:
            expiration_date = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # Features par défaut
        default_features = {
            "workflow_engine": True,
            "math_engine": True,
            "document_engine": True,
            "knowledge_engine": True,
            "api_access": True,
            "multi_user": max_users > 1,
            "reporting": True,
            "support": license_type in ["premium", "enterprise"]
        }
        
        if features:
            default_features.update(features)
        
        # Créer l'objet licence
        license_data = {
            "license_key": license_key,
            "customer": {
                "name": customer_name,
                "email": customer_email
            },
            "product": product,
            "version": "7.1.0",
            "type": license_type,
            "max_users": max_users,
            "issued_at": datetime.now().isoformat(),
            "expires_at": expiration_date,
            "validation_hash": validation_hash,
            "salt": salt,
            "features": default_features,
            "status": "active"
        }
        
        return license_data
    
    def validate_license(self, license_key: str, customer_email: str) -> bool:
        """Valider une clé de licence."""
        # En production: vérifier dans la base de données ou le fichier JSON
        try:
            with open(self.license_database, 'r') as f:
                licenses = json.load(f)
            
            for lic in licenses:
                if lic["license_key"] == license_key:
                    # Vérifier le hash
                    validation_hash = self.generate_hash(customer_email, lic["salt"])
                    return validation_hash == lic["validation_hash"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return False
    
    def save_license(self, license_data: Dict[str, Any]) -> bool:
        """Sauvegarder une licence dans la base de données."""
        try:
            licenses = []
            if self.license_database.exists():
                with open(self.license_database, 'r') as f:
                    licenses = json.load(f)
            
            licenses.append(license_data)
            
            with open(self.license_database, 'w') as f:
                json.dump(licenses, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def export_license(self, license_data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Exporter une licence dans un fichier ou retourner comme JSON."""
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            return f"Licence exportée vers {output_file}"
        else:
            return json.dumps(license_data, indent=2)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="SMART_AO V7 - Générateur de clés de licence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python generate_license_key.py --name "Société ABC" --email "contact@abc.fr"
  python generate_license_key.py --name "Client" --email "client@test.com" --type premium --users 50
        """
    )
    
    parser.add_argument("--name", "-n", required=True, help="Nom du client")
    parser.add_argument("--email", "-e", required=True, help="Email du client")
    parser.add_argument("--type", "-t", default="standard", 
                        choices=["trial", "standard", "premium", "enterprise"],
                        help="Type de licence")
    parser.add_argument("--product", "-p", default="SMART_AO_V7", help="Nom du produit")
    parser.add_argument("--users", "-u", type=int, default=10, help="Nombre maximum d'utilisateurs")
    parser.add_argument("--days", "-d", type=int, default=365, help="Durée de validité en jours")
    parser.add_argument("--output", "-o", help="Fichier de sortie pour la licence")
    parser.add_argument("--no-save", action="store_true", help="Ne pas sauvegarder dans la base")
    
    args = parser.parse_args()
    
    # Créer le générateur
    generator = LicenseGenerator()
    
    # Créer la licence
    license_data = generator.create_license(
        customer_name=args.name,
        customer_email=args.email,
        product=args.product,
        license_type=args.type,
        max_users=args.users,
        expires_in_days=args.days
    )
    
    # Afficher la clé de licence
    print("\n" + "=" * 60)
    print("SMART_AO V7 - Générateur de Licence")
    print("=" * 60)
    print(f"\nClient: {args.name}")
    print(f"Email: {args.email}")
    print(f"Type: {args.type}")
    print(f"Utilisateurs: {args.users}")
    print(f"Validité: {args.days} jours")
    print(f"\nClé de Licence: {license_data['license_key']}")
    print("=" * 60 + "\n")
    
    # Sauvegarder si demandé
    if not args.no_save:
        if generator.save_license(license_data):
            print("✓ Licence sauvegardée dans la base de données")
        else:
            print("⚠ Échec de la sauvegarde")
    
    # Exporter
    output_message = generator.export_license(license_data, args.output)
    print(output_message)


if __name__ == "__main__":
    main()


