"""Email Engine - Envoi de notifications email transactionnelles"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailEngine:
    """Moteur d'envoi d'emails transactionnels"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST or "localhost"
        self.smtp_port = settings.SMTP_PORT or 587
        self.from_email = settings.FROM_EMAIL or "noreply@smart-ao.fr"
    
    def send_email(
        self,
        to: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """Envoie un email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to
            
            if not body_text:
                body_text = "Votre client email ne supporte pas le HTML"
            
            part1 = MIMEText(body_text, "plain", "utf-8")
            part2 = MIMEText(body_html, "html", "utf-8")
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envoi (désactivé en dev sans SMTP)
            if settings.ENVIRONMENT == "production":
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    if settings.SMTP_USER:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(self.from_email, [to], msg.as_string())
            
            logger.info(f"Email envoyé à {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Échec envoi email: {str(e)}")
            return False
    
    def send_deadline_alert(
        self,
        recipient: str,
        mission_name: str,
        deadline_date: str,
        days_remaining: int
    ):
        """Envoie une alerte deadline"""
        urgency = "URGENT" if days_remaining <= 2 else "Rappel"
        subject = f"[{urgency}] Deadline AO: {mission_name} - J-{days_remaining}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {'red' if days_remaining <= 2 else 'orange'};">
                {urgency} - Deadline Approche
            </h2>
            <p><strong>Mission:</strong> {mission_name}</p>
            <p><strong>Date limite:</strong> {deadline_date}</p>
            <p><strong>Temps restant:</strong> {days_remaining} jours</p>
            <hr>
            <p style="color: gray;">SMART_AO - Analyse d'Appels d'Offres BTP</p>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, html_body)
    
    def send_report_ready(
        self,
        recipient: str,
        mission_name: str,
        report_url: str,
        summary: Dict
    ):
        """Envoie la notification de rapport prêt"""
        subject = f"✅ Rapport d'analyse prêt: {mission_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: green;">Analyse Terminée</h2>
            <p><strong>Mission:</strong> {mission_name}</p>
            <ul>
                <li>Points critiques: {summary.get('critical_points', 0)}</li>
                <li>Pénalités détectées: {summary.get('penalites', 0)}</li>
                <li>Score global: {summary.get('score', 'N/A')}</li>
            </ul>
            <a href="{report_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Voir le rapport complet
            </a>
        </body>
        </html>
        """
        
        return self.send_email(recipient, subject, html_body)

# Instance globale
email_engine = EmailEngine()
