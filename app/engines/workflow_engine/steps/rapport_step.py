"""
SMART_AO V7 - rapport_step.py
=============================
Étape 6 : Génération du rapport final et des livrables.
Produit le rapport d'analyse complet pour l'utilisateur.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from app.engines.workflow_engine.steps.base_step import BaseStep

logger = logging.getLogger(__name__)


class RapportStep(BaseStep):
    """Étape de génération du rapport final."""

    name = "rapport_step"
    version = "1.0.0"
    description = "Génération du rapport d'analyse final et des livrables pour l'utilisateur"

    async def execute(self, mission_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère le rapport final à partir des données compilées.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant le rapport compilé
            
        Returns:
            Dict avec le rapport final formaté et les livrables
        """
        logger.info(f"[{self.name}] Démarrage de la génération du rapport pour la mission {mission_id}")
        
        try:
            compiled_report = context.get("compiled_report", {})
            if not compiled_report:
                raise ValueError("Aucun rapport compilé à transformer")

            # Génération du rapport final
            final_report = {
                "report_id": f"RPT-{mission_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "mission_id": mission_id,
                "version": "1.0",
                "executive_summary": self._generate_executive_summary(compiled_report),
                "detailed_analysis": self._format_detailed_analysis(compiled_report),
                "action_plan": self._generate_action_plan(compiled_report),
                "annexes": self._prepare_annexes(compiled_report),
                "metadata": {
                    "total_alertes": len(compiled_report.get("alertes", [])),
                    "total_recommandations": len(compiled_report.get("recommandations", [])),
                    "agents_contributors": list(compiled_report.get("analyses", {}).keys())
                }
            }

            # Préparation des livrables
            deliverables = {
                "rapport_json": final_report,
                "rapport_text": self._generate_text_report(final_report),
                "checklist_actions": self._generate_checklist(final_report),
                "synthese_executive": final_report["executive_summary"]
            }

            result = {
                "status": "success",
                "final_report": final_report,
                "deliverables": deliverables,
                "workflow_completed": True,
                "next_step": None
            }

            logger.info(f"[{self.name}] Rapport généré avec succès - ID: {final_report['report_id']}")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] Erreur critique lors de la génération du rapport : {str(e)}")
            return {
                "status": "error",
                "error_code": "RAPPORT_GENERATION_FAILED",
                "error_message": str(e),
                "next_step": None
            }

    def _generate_executive_summary(self, compiled_report: Dict) -> Dict[str, Any]:
        """Génère le résumé exécutif du rapport."""
        alertes = compiled_report.get("alertes", [])
        recommandations = compiled_report.get("recommandations", [])
        
        # Calcul du score global de risque
        risk_score = self._calculate_risk_score(alertes)
        
        return {
            "risk_level": self._get_risk_level(risk_score),
            "risk_score": risk_score,
            "critical_alertes_count": sum(1 for a in alertes if a.get("niveau") == "high"),
            "major_recommandations_count": len(recommandations),
            "go_no_go_recommendation": "NO-GO" if risk_score > 70 else "GO" if risk_score < 30 else "GO_WITH_RESERVES",
            "key_points": [
                f"{len(alertes)} alertes identifiées",
                f"{len(recommandations)} recommandations émises",
                f"Niveau de risque : {self._get_risk_level(risk_score)}"
            ]
        }

    def _format_detailed_analysis(self, compiled_report: Dict) -> Dict[str, Any]:
        """Formate l'analyse détaillée pour le rapport."""
        analyses = compiled_report.get("analyses", {})
        
        formatted = {}
        for agent_name, analysis_data in analyses.items():
            formatted[agent_name] = {
                "title": self._get_agent_title(agent_name),
                "findings": analysis_data,
                "confidence_level": "high"  # À calculer dynamiquement
            }
        
        return formatted

    def _generate_action_plan(self, compiled_report: Dict) -> List[Dict]:
        """Génère un plan d'action priorisé."""
        action_plan = []
        priority = 1
        
        # Actions basées sur les alertes critiques
        for alerte in compiled_report.get("alertes", []):
            if alerte.get("niveau") == "high":
                action_plan.append({
                    "priority": priority,
                    "type": "urgent",
                    "description": f"Traiter l'alerte critique : {alerte.get('content', 'N/A')}",
                    "source": alerte.get("source_agent", "unknown"),
                    "deadline": "Immédiat"
                })
                priority += 1
        
        # Actions basées sur les recommandations
        for reco in compiled_report.get("recommandations", [])[:5]:  # Top 5
            action_plan.append({
                "priority": priority,
                "type": "recommendation",
                "description": reco.get("content", "N/A"),
                "source": reco.get("source_agent", "unknown"),
                "deadline": "Sous 7 jours"
            })
            priority += 1
        
        return action_plan

    def _prepare_annexes(self, compiled_report: Dict) -> List[Dict]:
        """Prépare les annexes du rapport."""
        annexes = []
        
        # Annexe : Liste complète des alertes
        annexes.append({
            "title": "Liste complète des alertes",
            "content": compiled_report.get("alertes", []),
            "type": "alertes"
        })
        
        # Annexe : Recommandations détaillées
        annexes.append({
            "title": "Recommandations détaillées",
            "content": compiled_report.get("recommandations", []),
            "type": "recommandations"
        })
        
        return annexes

    def _generate_text_report(self, final_report: Dict) -> str:
        """Génère une version texte du rapport."""
        lines = [
            "=" * 80,
            "RAPPORT D'ANALYSE SMART_AO V7",
            "=" * 80,
            f"ID: {final_report.get('report_id', 'N/A')}",
            f"Généré le: {final_report.get('generated_at', 'N/A')}",
            "",
            "SYNTHÈSE EXÉCUTIVE",
            "-" * 40,
        ]
        
        summary = final_report.get("executive_summary", {})
        lines.append(f"Niveau de risque : {summary.get('risk_level', 'N/A')}")
        lines.append(f"Recommandation : {summary.get('go_no_go_recommendation', 'N/A')}")
        lines.append("")
        
        lines.append("PLAN D'ACTION PRIORITAIRE")
        lines.append("-" * 40)
        for action in final_report.get("action_plan", [])[:5]:
            lines.append(f"  [{action.get('priority')}] {action.get('description', 'N/A')}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)

    def _generate_checklist(self, final_report: Dict) -> List[Dict]:
        """Génère une checklist d'actions à mener."""
        checklist = []
        
        for action in final_report.get("action_plan", []):
            checklist.append({
                "action": action.get("description", ""),
                "completed": False,
                "priority": action.get("priority", 99),
                "type": action.get("type", "general")
            })
        
        return sorted(checklist, key=lambda x: x["priority"])

    def _calculate_risk_score(self, alertes: List[Dict]) -> int:
        """Calcule un score de risque de 0 à 100."""
        score = 0
        for alerte in alertes:
            niveau = alerte.get("niveau", "low")
            if niveau == "high":
                score += 20
            elif niveau == "medium":
                score += 10
            else:
                score += 5
        return min(score, 100)

    def _get_risk_level(self, score: int) -> str:
        """Traduit le score en niveau de risque."""
        if score >= 70:
            return "CRITIQUE"
        elif score >= 40:
            return "ÉLEVÉ"
        elif score >= 20:
            return "MODÉRÉ"
        else:
            return "FAIBLE"

    def _get_agent_title(self, agent_name: str) -> str:
        """Retourne le titre humain d'un agent."""
        titles = {
            "agent_deadline": "Analyse des Deadlines",
            "agent_pab": "Détection PAB",
            "agent_penalites": "Analyse des Pénalités",
            "agent_risque": "Évaluation des Risques",
            "agent_synthese": "Synthèse Globale"
        }
        return titles.get(agent_name, agent_name.replace("_", " ").title())

    async def rollback(self, mission_id: str, context: Dict[str, Any]) -> bool:
        """Nettoie le rapport généré en cas d'échec global."""
        logger.warning(f"[{self.name}] Rollback demandé pour mission {mission_id}")
        return True
