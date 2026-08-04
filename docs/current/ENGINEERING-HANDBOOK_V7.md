# SMART_AO V7 - ENGINEERING HANDBOOK
**58 ADR + 11 solveurs + 31/38 gates**

## ADR (Architecture Decision Records)

### ADR-042: Agent Registry Decorator Pattern
- **Status:** Accepted
- **Context:** Besoin d'un systeme flexible pour enregistrer les agents
- **Decision:** Utiliser un decorator @registry.register()
- **Consequences:** Simplifie l'ajout d'agents, evite les imports circulaires

### ADR-043: Async SQLAlchemy
- **Status:** Accepted
- **Context:** Application FastAPI async
- **Decision:** SQLAlchemy async avec asyncpg
- **Consequences:** Meilleure performance, compatibilite async

### ADR-044: BaseAgent Contract
- **Status:** Accepted
- **Context:** Interface unifiee pour tous les agents
- **Decision:** BaseAgent avec can_handle() et execute()
- **Consequences:** Facilite le testing et l'integration

### ADR-045: Event-Driven Architecture
- **Status:** Accepted
- **Context:** Decouplage des composants
- **Decision:** EventBus pour toute communication
- **Consequences:** Decouplage total, facilite debug et replay

### ADR-046: Zero LLM in Core
- **Status:** Accepted
- **Context:** Reduire les couts et dependances
- **Decision:** Aucune LLM dans le code core
- **Consequences:** Coûts reduits, fiabilite amelioree

## 11 SOLVEURS

Voir Math Engine pour la liste complete des solveurs:
1. chiffrage_pulp.py
2. decimal_ops.py
3. treasury.py
4. margin.py
5. planning.py
6. worst_case.py
7. penalites_cumul.py
8. rep_cost.py
9. site_coeff.py
10. capacite_financiere.py
11. risques_generator.py

## BEST PRACTICES

### Code Quality
- Respecter les contrats BaseAgent
- Utiliser les decorators @registry.register
- Documenter chaque capability
- Tests unitaire pour chaque agent

### Security
- Toujours verifier les inputs
- Utiliser RBAC pour l'acces aux donnees
- Audit WORM pour toutes les operations critiques
- Isolation des workers (Docling 6Go)

### Performance
- Limiter le parallelisme a 6 agents
- Utiliser async/await partout
- Cache les resultats de recherche
- Optimiser les requetes SQL

## STATUT

- Phase 0: 100% COMPLETE
- ADR: 58+ decisions documentees
- Solveurs: 11 implementees
- Gates: 31/38 validees

**Date:** 04.08.2026
**Version:** V7
