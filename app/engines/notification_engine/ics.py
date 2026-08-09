"""ICS Generator - Génération de fichiers calendrier pour deadlines"""
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ICSGenerator:
    """Génère des fichiers .ics pour les calendriers"""
    
    def generate_deadline_ics(
        self,
        mission_name: str,
        deadline: datetime,
        description: str = "",
        location: str = "",
        uid: Optional[str] = None
    ) -> str:
        """Génère un événement ICS pour une deadline"""
        uid = uid or f"mission-{datetime.utcnow().timestamp()}@smart-ao.fr"
        
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SMART_AO//FR
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{deadline.strftime('%Y%m%dT090000Z')}
DTEND:{deadline.strftime('%Y%m%dT180000Z')}
SUMMARY:Deadline AO - {mission_name}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:Rappel Deadline
END:VALARM
END:VEVENT
END:VCALENDAR
"""
        return ics_content
    
    def generate_meeting_ics(
        self,
        subject: str,
        start: datetime,
        end: datetime,
        attendees: list,
        location: str = ""
    ) -> str:
        """Génère un événement de réunion"""
        uid = f"meeting-{datetime.utcnow().timestamp()}@smart-ao.fr"
        attendees_str = "\n".join([f"ATTENDEE:mailto:{a}" for a in attendees])
        
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SMART_AO//FR
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{subject}
LOCATION:{location}
ORGANIZER:mailto:noreply@smart-ao.fr
{attendees_str}
END:VEVENT
END:VCALENDAR
"""
        return ics_content

# Instance globale
ics_generator = ICSGenerator()
