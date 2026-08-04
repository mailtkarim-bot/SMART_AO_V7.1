"""
SMART_AO V7 - Event Bus Models
Source: ARCHITECTURE_V7_ENGINE.md §5

Centralise les modèles Event pour le Event Bus V7
SSoT: Single Source of Truth pour les events système
"""

# Réexport depuis les implémentations concrètes
# Event Pydantic (pour API/Bus) depuis bus.py
# EventType SQLAlchemy (pour persistance) depuis app.models.events

from app.engines.event_bus.bus import Event
from app.models.events import EventType

# Tout ce qui est exporté ici est disponible via:
# from app.engines.event_bus.models import Event, EventType

__all__ = ["Event", "EventType"]

