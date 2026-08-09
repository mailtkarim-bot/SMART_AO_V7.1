"""Deadline Monitor - Surveillance des deadlines avec escalade automatique"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.mission import Mission
from app.engines.notification_engine.email import email_engine

logger = logging.getLogger(__name__)

class DeadlineMonitor:
    """Surveille les deadlines et déclenche les alertes"""
    
    ALERT_SCHEDULE = [7, 5, 3, 2, 1, 0]  # Jours avant deadline
    
    def __init__(self):
        self.last_alerts = {}  # Cache pour éviter les doublons
    
    def check_all_deadlines(self, db: Session):
        """Vérifie toutes les missions actives"""
        missions = db.query(Mission).filter(
            Mission.status.in_(["processing", "pending_review"])
        ).all()
        
        alerts_sent = []
        for mission in missions:
            if mission.deadline_date:
                alert = self._check_single_deadline(mission)
                if alert:
                    alerts_sent.append(alert)
        
        return alerts_sent
    
    def _check_single_deadline(self, mission: Mission) -> Optional[Dict]:
        """Vérifie une mission spécifique"""
        today = datetime.utcnow().date()
        days_remaining = (mission.deadline_date - today).days
        
        if days_remaining not in self.ALERT_SCHEDULE:
            return None
        
        # Éviter les doublons
        cache_key = f"{mission.id}_{days_remaining}"
        if cache_key in self.last_alerts:
            return None
        
        # Envoyer alerte
        user_email = mission.user.email if hasattr(mission.user, 'email') else None
        if user_email:
            email_engine.send_deadline_alert(
                recipient=user_email,
                mission_name=mission.name,
                deadline_date=mission.deadline_date.isoformat(),
                days_remaining=days_remaining
            )
            
            self.last_alerts[cache_key] = datetime.utcnow()
            
            return {
                "mission_id": mission.id,
                "days_remaining": days_remaining,
                "alert_type": "deadline",
                "sent_at": datetime.utcnow().isoformat()
            }
        
        return None
    
    def get_urgent_missions(self, db: Session, threshold_days: int = 3) -> List[Mission]:
        """Récupère les missions urgentes"""
        today = datetime.utcnow().date()
        threshold_date = today + timedelta(days=threshold_days)
        
        return db.query(Mission).filter(
            Mission.status.in_(["processing", "pending_review"]),
            Mission.deadline_date <= threshold_date,
            Mission.deadline_date >= today
        ).all()

# Instance globale
deadline_monitor = DeadlineMonitor()
