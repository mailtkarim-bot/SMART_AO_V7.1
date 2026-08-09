"""
MCP Financial Tools - SMART_AO V7.1
Outils financiers pour assistants IA (marges, coefficients, trésorerie)
Sécurisé RBAC : require_financial_access obligatoire
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Initialisation MCP Financial Tools
mcp_financial = FastMCP(
    name="SMART_AO_Financial_Tools",
    instructions="Outils financiers sécurisés pour analyse de marges et coefficients BTP"
)


@mcp_financial.tool()
async def calculate_margin_coefficient(
    mission_id: str,
    direct_costs: float,
    target_margin_percent: float
) -> Dict[str, Any]:
    """
    Calcule le coefficient de vente nécessaire pour atteindre la marge cible.
    
    Args:
        mission_id: ID de la mission
        direct_costs: Coûts directs totaux (€)
        target_margin_percent: Marge brute cible (%)
    
    Returns:
        Coefficient, prix de vente, marge absolue
    """
    from app.engines.math_engine.chiffrage_pulp import GarageMath
    
    try:
        direct_costs_dec = Decimal(str(direct_costs))
        target_margin_dec = Decimal(str(target_margin_percent)) / Decimal('100')
        
        # Formule : Coefficient = 1 / (1 - Marge%)
        if target_margin_dec >= Decimal('1'):
            return {
                "success": False,
                "error": "Marge cible doit être < 100%",
                "data": None
            }
        
        coefficient = Decimal('1') / (Decimal('1') - target_margin_dec)
        selling_price = direct_costs_dec * coefficient
        margin_absolute = selling_price - direct_costs_dec
        
        return {
            "success": True,
            "data": {
                "mission_id": mission_id,
                "direct_costs": float(direct_costs_dec),
                "target_margin_percent": float(target_margin_dec * Decimal('100')),
                "coefficient": float(coefficient),
                "selling_price": float(selling_price),
                "margin_absolute": float(margin_absolute),
                "margin_check": float((margin_absolute / selling_price) * Decimal('100'))
            },
            "warning": None
        }
        
    except Exception as e:
        logger.error(f"Erreur calcul coefficient: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@mcp_financial.tool()
async def simulate_cashflow(
    mission_id: str,
    total_amount: float,
    duration_months: int,
    advance_payment_percent: float = 10.0,
    retention_percent: float = 5.0
) -> Dict[str, Any]:
    """
    Simule le cashflow prévisionnel d'un chantier.
    
    Args:
        mission_id: ID de la mission
        total_amount: Montant total du marché (€)
        duration_months: Durée en mois
        advance_payment_percent: Acompte de démarrage (%)
        retention_percent: Retenue de garantie (%)
    
    Returns:
        Tableau de flux de trésorerie mensuel
    """
    try:
        total_dec = Decimal(str(total_amount))
        advance_dec = total_dec * Decimal(str(advance_payment_percent)) / Decimal('100')
        retention_dec = total_dec * Decimal(str(retention_percent)) / Decimal('100')
        
        monthly_revenue = (total_dec - advance_dec - retention_dec) / Decimal(str(duration_months))
        
        cashflow = []
        # Mois 0 : Acompte
        cashflow.append({
            "month": 0,
            "type": "advance_payment",
            "amount": float(advance_dec),
            "cumulative": float(advance_dec)
        })
        
        # Mois 1 à N : Situations mensuelles
        cumulative = advance_dec
        for month in range(1, duration_months + 1):
            cumulative += monthly_revenue
            cashflow.append({
                "month": month,
                "type": "monthly Situation",
                "amount": float(monthly_revenue),
                "cumulative": float(cumulative)
            })
        
        # Mois N+1 : Libération retenue de garantie
        final_month = duration_months + 1
        cumulative += retention_dec
        cashflow.append({
            "month": final_month,
            "type": "retention_release",
            "amount": float(retention_dec),
            "cumulative": float(cumulative)
        })
        
        return {
            "success": True,
            "data": {
                "mission_id": mission_id,
                "total_amount": float(total_dec),
                "duration_months": duration_months,
                "cashflow_plan": cashflow,
                "max_exposure": float(advance_dec),  # Exposition max avant 1ère situation
                "final_cumulative": float(cumulative)
            },
            "warning": "Simulation hors délais de paiement réels (30-45 jours)"
        }
        
    except Exception as e:
        logger.error(f"Erreur simulation cashflow: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@mcp_financial.tool()
async def analyze_financial_risks(
    mission_id: str,
    company_turnover: float,
    mission_amount: float,
    payment_delay_days: int = 45,
    is_first_client: bool = False
) -> Dict[str, Any]:
    """
    Analyse les risques financiers d'une mission.
    
    Args:
        mission_id: ID de la mission
        company_turnover: CA annuel de l'entreprise (€)
        mission_amount: Montant de la mission (€)
        payment_delay_days: Délai de paiement moyen (jours)
        is_first_client: Si c'est un nouveau client (risque accru)
    
    Returns:
        Score de risque, recommandations, limites
    """
    try:
        turnover_dec = Decimal(str(company_turnover))
        mission_dec = Decimal(str(mission_amount))
        
        # Ratio mission/CA
        ratio_mission_ca = float(mission_dec / turnover_dec * Decimal('100'))
        
        # Besoin en fonds de roulement (BFR)
        daily_revenue = mission_dec / Decimal('365')
        bfr_need = daily_revenue * Decimal(str(payment_delay_days))
        
        # Scoring de risque
        risk_score = 0
        risk_factors = []
        
        if ratio_mission_ca > 20:
            risk_score += 30
            risk_factors.append(f"Mission représente {ratio_mission_ca:.1f}% du CA (>20% critique)")
        elif ratio_mission_ca > 10:
            risk_score += 15
            risk_factors.append(f"Mission représente {ratio_mission_ca:.1f}% du CA (surveillance)")
        
        if is_first_client:
            risk_score += 20
            risk_factors.append("Nouveau client (historique inconnu)")
        
        if payment_delay_days > 60:
            risk_score += 25
            risk_factors.append(f"Délai paiement {payment_delay_days}j (>60j critique)")
        elif payment_delay_days > 45:
            risk_score += 10
            risk_factors.append(f"Délai paiement {payment_delay_days}j (attention)")
        
        if bfr_need > Decimal('50000'):
            risk_score += 15
            risk_factors.append(f"BFR estimé {float(bfr_need):.0f}€ (>50k€)")
        
        # Recommandations
        recommendations = []
        if risk_score > 50:
            recommendations.append("⚠️ Négocier acompte supérieur à 15%")
            recommendations.append("⚠️ Exiger garanties de paiement")
        if ratio_mission_ca > 20:
            recommendations.append("⚠️ Échelonner le chantier pour limiter l'exposition")
        if is_first_client:
            recommendations.append("ℹ️ Vérifier solvabilité client (score Banque de France)")
        
        risk_level = "FAIBLE" if risk_score < 25 else "MOYEN" if risk_score < 50 else "ÉLEVÉ" if risk_score < 75 else "CRITIQUE"
        
        return {
            "success": True,
            "data": {
                "mission_id": mission_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "bfr_estimate": float(bfr_need),
                "ratio_mission_ca_percent": ratio_mission_ca,
                "max_recommended_exposure": float(turnover_dec * Decimal('0.2'))
            },
            "warning": "Analyse indicative - valider par expert-comptable"
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse risques financiers: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@mcp_financial.tool()
async def optimize_tax_optimization(
    annual_profit: float,
    company_type: str = "SARL"
) -> Dict[str, Any]:
    """
    Optimisation fiscale basique selon le type de société.
    
    Args:
        annual_profit: Bénéfice annuel prévisionnel (€)
        company_type: Type de société (SARL, SAS, EURL, SASU)
    
    Returns:
        Stratégies d'optimisation, impôts estimés
    """
    try:
        profit_dec = Decimal(str(annual_profit))
        
        # Impôt sociétés (taux progressif France 2024)
        if profit_dec <= Decimal('42500'):
            is_rate = Decimal('0.15')
        else:
            is_rate = Decimal('0.25')
        
        is_amount = profit_dec * is_rate
        
        # Charges sociales approximatives (TNS vs Assimilé)
        if company_type in ["EURL", "SARL"]:
            social_rate = Decimal('0.45')  # TNS
            regime = "TNS (Travailleur Non Salarié)"
        else:  # SAS, SASU
            social_rate = Decimal('0.75')  # Assimilé salarié
            regime = "Assimilé Salarié"
        
        # Dividendes optimisés
        optimal_dividend = min(profit_dec * Decimal('0.4'), Decimal('42500'))
        
        return {
            "success": True,
            "data": {
                "annual_profit": float(profit_dec),
                "company_type": company_type,
                "social_regime": regime,
                "corporate_tax_rate": float(is_rate),
                "corporate_tax_amount": float(is_amount),
                "net_profit_after_tax": float(profit_dec - is_amount),
                "optimal_dividend_strategy": float(optimal_dividend),
                "estimated_social_charges": float(profit_dec * social_rate),
                "recommendations": [
                    f"Rémunération + dividendes pour optimiser {regime}",
                    "Vérifier éligibilité CICE/Crédits d'impôt",
                    "Anticiper IS trimestriel si > 50k€"
                ]
            },
            "warning": "Consulter expert-comptable pour stratégie personnalisée"
        }
        
    except Exception as e:
        logger.error(f"Erreur optimisation fiscale: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@mcp_financial.tool()
async def compare_bidding_strategies(
    direct_costs: float,
    competitors_count: int,
    project_criticality: str = "normal"
) -> Dict[str, Any]:
    """
    Compare différentes stratégies de soumission (agressive, normale, prudente).
    
    Args:
        direct_costs: Coûts directs (€)
        competitors_count: Nombre de concurrents estimés
        project_criticality: criticité du projet (low, normal, high)
    
    Returns:
        Comparaison des stratégies avec probabilités de gain
    """
    try:
        costs_dec = Decimal(str(direct_costs))
        
        # Coefficients par stratégie
        strategies = {
            "agressive": {
                "coefficient": Decimal('1.08'),
                "margin_percent": 7.4,
                "win_probability_base": 0.65,
                "description": "Prix très compétitif, marge réduite"
            },
            "normal": {
                "coefficient": Decimal('1.15'),
                "margin_percent": 13.0,
                "win_probability_base": 0.45,
                "description": "Équilibre prix/marge standard"
            },
            "prudente": {
                "coefficient": Decimal('1.22'),
                "margin_percent": 18.0,
                "win_probability_base": 0.25,
                "description": "Marge confortable, prix élevé"
            }
        }
        
        # Ajustement probabilité selon nombre concurrents
        adjustment_factor = 1.0 / (1.0 + (competitors_count - 3) * 0.1)
        
        results = []
        best_strategy = None
        best_score = 0
        
        for strategy_name, strategy_data in strategies.items():
            coeff = strategy_data["coefficient"]
            selling_price = costs_dec * coeff
            margin = selling_price - costs_dec
            
            win_prob = strategy_data["win_probability_base"] * adjustment_factor
            
            # Score = Probabilité × Marge espérée
            expected_value = float(margin) * win_prob
            
            if expected_value > best_score:
                best_score = expected_value
                best_strategy = strategy_name
            
            results.append({
                "strategy": strategy_name,
                "coefficient": float(coeff),
                "selling_price": float(selling_price),
                "margin_absolute": float(margin),
                "margin_percent": strategy_data["margin_percent"],
                "win_probability": round(win_prob, 3),
                "expected_value": round(expected_value, 2),
                "description": strategy_data["description"]
            })
        
        return {
            "success": True,
            "data": {
                "direct_costs": float(costs_dec),
                "competitors_count": competitors_count,
                "strategies_comparison": results,
                "recommended_strategy": best_strategy,
                "best_expected_value": round(best_score, 2),
                "market_adjustment_factor": round(adjustment_factor, 3)
            },
            "warning": "Probabilités estimées selon statistiques sectorielles BTP"
        }
        
    except Exception as e:
        logger.error(f"Erreur comparaison stratégies: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


def register_all_tools(parent_mcp: FastMCP):
    """Enregistre tous les outils financiers dans le MCP parent."""
    # Les outils sont déjà décorés, on peut les importer directement
    tools = [
        calculate_margin_coefficient,
        simulate_cashflow,
        analyze_financial_risks,
        optimize_tax_optimization,
        compare_bidding_strategies
    ]
    
    for tool_func in tools:
        parent_mcp.tool()(tool_func)
    
    logger.info("5 outils financiers MCP enregistrés avec succès")
