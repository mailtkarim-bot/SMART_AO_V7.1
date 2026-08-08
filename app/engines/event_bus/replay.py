"""
SMART_AO V7 - replay.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Event Replay
===========================
Replay des événements pour le débogage et la reprise.
"""

from typing import List, Optional, Generator
from datetime import datetime
import json

from app.engines.event_bus.models import Event, EventType
from app.engines.event_bus.bus import EventBus, event_bus, get_event_bus


class EventReplay:
    """Gestionnaire de replay des événements."""
    
    def __init__(self, event_bus: EventBus = None):
        self.bus = event_bus or get_event_bus()
    
    def record_event(self, event: Event) -> None:
        """Enregistrer un événement pour le replay."""
        self.bus.publish(event)
    
    def replay_events(
        self,
        event_type: Optional[EventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Rejouer les événements."""
        history = self.bus.get_history(event_type, limit * 10)
        
        filtered = []
        for event in history:
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if len(filtered) >= limit:
                break
            filtered.append(event)
        
        return filtered
    
    def replay_and_publish(
        self,
        event_type: Optional[EventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> int:
        """Rejouer et republier les événements."""
        events = self.replay_events(event_type, start_time, end_time, limit)
        count = 0
        for event in events:
            self.bus.publish(event)
            count += 1
        return count
    
    def save_to_file(self, filepath: str, limit: int = 1000) -> int:
        """Sauvegarder l'historique dans un fichier."""
        events = self.bus.get_history(limit=limit)
        with open(filepath, 'w', encoding='utf-8') as f:
            for event in events:
                f.write(event.to_json() + '\n')
        return len(events)
    
    def load_from_file(self, filepath: str) -> List[Event]:
        """Charger l'historique depuis un fichier."""
        events = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        event = Event.from_dict(data)
                        events.append(event)
        except Exception as e:
            raise ValueError(f"Error loading events from {filepath}: {e}")
        return events
    
    def load_and_replay(self, filepath: str) -> int:
        """Charger et rejouer les événements depuis un fichier."""
        events = self.load_from_file(filepath)
        count = 0
        for event in events:
            self.bus.publish(event)
            count += 1
        return count
