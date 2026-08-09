#!/usr/bin/env python3
"""
SMART_AO V7 - Agent Update Script
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Script de mise à jour des agents pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §5.1

Ce script permet de:
- Lister les agents disponibles
- Mettre à jour les configurations des agents
- Activer/désactiver des agents
- Vérifier l'état des agents
"""

import argparse
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentManager:
    """Gestionnaire des agents SMART_AO V7."""
    
    def __init__(self, agents_dir: Path = None):
        self.agents_dir = agents_dir or Path("app/agents")
        self.agents_config = Path("config/agents.json")
        
    def list_agents(self) -> List[Dict[str, Any]]:
        """Lister tous les agents disponibles."""
        agents = []
        
        if not self.agents_dir.exists():
            logger.warning(f"Répertoire des agents non trouvé: {self.agents_dir}")
            return agents
        
        for agent_file in self.agents_dir.glob("*.py"):
            if agent_file.name != "__init__.py":
                agents.append({
                    "name": agent_file.stem,
                    "path": str(agent_file),
                    "loaded": False
                })
        
        return agents
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Récupérer les informations d'un agent spécifique."""
        try:
            # En production: importer dynamiquement l'agent
            module_path = f"app.agents.{agent_name}"
            module = __import__(module_path, fromlist=["Agent"])
            
            if hasattr(module, "Agent"):
                agent_class = module.Agent
                return {
                    "name": agent_name,
                    "class": agent_class.__name__,
                    "description": getattr(agent_class, "__doc__", ""),
                    "status": "available"
                }
        except Exception as e:
            logger.error(f"Erreur chargement agent {agent_name}: {e}")
        
        return None
    
    def load_agents_config(self) -> Dict[str, Any]:
        """Charger la configuration des agents."""
        if self.agents_config.exists():
            try:
                with open(self.agents_config, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement config: {e}")
        
        return {"agents": {}}
    
    def save_agents_config(self, config: Dict[str, Any]) -> bool:
        """Sauvegarder la configuration des agents."""
        try:
            self.agents_config.parent.mkdir(parents=True, exist_ok=True)
            with open(self.agents_config, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")
            return False
    
    def enable_agent(self, agent_name: str) -> bool:
        """Activer un agent."""
        config = self.load_agents_config()
        
        if agent_name not in config["agents"]:
            config["agents"][agent_name] = {}
        
        config["agents"][agent_name]["enabled"] = True
        config["agents"][agent_name]["updated_at"] = datetime.now().isoformat()
        
        return self.save_agents_config(config)
    
    def disable_agent(self, agent_name: str) -> bool:
        """Désactiver un agent."""
        config = self.load_agents_config()
        
        if agent_name in config["agents"]:
            config["agents"][agent_name]["enabled"] = False
            config["agents"][agent_name]["updated_at"] = datetime.now().isoformat()
        
        return self.save_agents_config(config)
    
    def update_agent_config(
        self,
        agent_name: str,
        new_config: Dict[str, Any]
    ) -> bool:
        """Mettre à jour la configuration d'un agent."""
        config = self.load_agents_config()
        
        if agent_name not in config["agents"]:
            config["agents"][agent_name] = {}
        
        config["agents"][agent_name].update(new_config)
        config["agents"][agent_name]["updated_at"] = datetime.now().isoformat()
        
        return self.save_agents_config(config)
    
    def check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Vérifier l'état de santé d'un agent."""
        try:
            agent_info = self.get_agent_info(agent_name)
            if agent_info:
                return {
                    "status": "healthy",
                    "agent": agent_name,
                    "loaded": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "agent": agent_name,
                    "error": "Agent non trouvé ou erreur de chargement"
                }
        except Exception as e:
            return {
                "status": "error",
                "agent": agent_name,
                "error": str(e)
            }


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="SMART_AO V7 - Gestionnaire de mise à jour des agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python update_agent.py --list
  python update_agent.py --enable workflow_agent
  python update_agent.py --disable old_agent
  python update_agent.py --check workflow_agent
  python update_agent.py --update workflow_agent --config '{"timeout": 30}'
        """
    )
    
    parser.add_argument("--list", "-l", action="store_true", help="Lister tous les agents")
    parser.add_argument("--enable", "-e", help="Activer un agent")
    parser.add_argument("--disable", "-d", help="Désactiver un agent")
    parser.add_argument("--check", "-c", help="Vérifier l'état d'un agent")
    parser.add_argument("--update", "-u", help="Mettre à jour la config d'un agent")
    parser.add_argument("--config", "-g", help="Configuration JSON à appliquer")
    parser.add_argument("--info", "-i", help="Afficher les infos d'un agent")
    
    args = parser.parse_args()
    
    # Créer le gestionnaire d'agents
    manager = AgentManager()
    
    if args.list:
        agents = manager.list_agents()
        print("\n" + "=" * 60)
        print("SMART_AO V7 - Agents Disponibles")
        print("=" * 60)
        
        if agents:
            for agent in agents:
                status = "✓" if agent.get("loaded") else "○"
                print(f"  {status} {agent['name']}")
        else:
            print("  Aucun agent trouvé")
        
        print("=" * 60 + "\n")
    
    elif args.enable:
        if manager.enable_agent(args.enable):
            print(f"✓ Agent {args.enable} activé")
        else:
            print(f"✗ Échec de l'activation de {args.enable}")
    
    elif args.disable:
        if manager.disable_agent(args.disable):
            print(f"✓ Agent {args.disable} désactivé")
        else:
            print(f"✗ Échec de la désactivation de {args.disable}")
    
    elif args.check:
        health = manager.check_agent_health(args.check)
        print("\n" + "=" * 60)
        print(f"État de santé: {args.check}")
        print("=" * 60)
        for key, value in health.items():
            print(f"  {key}: {value}")
        print("=" * 60 + "\n")
    
    elif args.info:
        info = manager.get_agent_info(args.info)
        if info:
            print("\n" + "=" * 60)
            print(f"Informations: {args.info}")
            print("=" * 60)
            for key, value in info.items():
                print(f"  {key}: {value}")
            print("=" * 60 + "\n")
        else:
            print(f"✗ Agent {args.info} non trouvé")
    
    elif args.update:
        config = {}
        if args.config:
            try:
                config = json.loads(args.config)
            except json.JSONDecodeError:
                print("✗ Configuration JSON invalide")
                return
        
        if manager.update_agent_config(args.update, config):
            print(f"✓ Configuration de {args.update} mise à jour")
        else:
            print(f"✗ Échec de la mise à jour")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


