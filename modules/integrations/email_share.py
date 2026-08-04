"""
modules/integrations/email_share.py
Email Share Integration for sending PDF evaluation reports via SMTP.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from utils.logger import logger

class EmailShare:
    @classmethod
    def send_report_email(
        cls,
        recipient_email: str,
        report_path: str,
        candidate_name: str = "Candidate",
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        sender_email: str = "",
        sender_password: str = ""
    ) -> bool:
        """Sends an evaluation report PDF as an email attachment."""
        if not os.path.exists(report_path):
            logger.error(f"[EmailShare] Report file not found: {report_path}")
            return False

        if not sender_email or not sender_password:
            logger.warning("[EmailShare] SMTP credentials missing.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"ResumeIQ Evaluation Report — {candidate_name}"

            body = (
                f"Hello,\n\n"
                f"Please find attached your ResumeIQ AI Executive Evaluation Report for {candidate_name}.\n\n"
                f"Best regards,\n"
                f"ResumeIQ Team"
            )
            msg.attach(MIMEText(body, 'plain'))

            with open(report_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(report_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_path)}"'
                msg.attach(part)

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"[EmailShare] Report sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"[EmailShare] Failed to send email: {e}")
            return False
