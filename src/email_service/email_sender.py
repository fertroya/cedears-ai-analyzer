"""
Servicio de envío de emails para reportes.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class EmailSender:
    """Envía reportes por email."""
    
    def __init__(self, config: dict):
        self.config = config
        email_config = config.get('email', {})
        
        self.smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = email_config.get('smtp_port', 587)
        self.use_tls = email_config.get('use_tls', True)
        
        # Obtener credenciales de variables de entorno
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.warning("Credenciales de email no configuradas. El envío de emails estará deshabilitado.")
    
    def send_report(
        self,
        html_content: str,
        subject: str,
        pdf_path: Optional[Path] = None
    ) -> bool:
        """
        Envía el reporte por email.
        
        Args:
            html_content: Contenido HTML del reporte
            subject: Asunto del email
            pdf_path: Ruta opcional al PDF adjunto
        
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.warning("No se puede enviar email: credenciales no configuradas")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Agregar HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Agregar PDF si existe
            if pdf_path and pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    pdf_part = MIMEBase('application', 'octet-stream')
                    pdf_part.set_payload(f.read())
                    encoders.encode_base64(pdf_part)
                    pdf_part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={pdf_path.name}'
                    )
                    msg.attach(pdf_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado exitosamente a {self.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email: {e}")
            return False
