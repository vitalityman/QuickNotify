import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
import logging
from datetime import datetime
import time

class MailSender:
    """Email sender using SMTP"""
    
    def __init__(self, smtp_config):
        """Initialize mail sender"""
        self.smtp_server = smtp_config.smtp_server
        self.smtp_port = smtp_config.smtp_port
        self.use_tls = smtp_config.use_tls
        self.sender_email = smtp_config.sender_email
        self.sender_password = smtp_config.sender_password
        self.timeout = smtp_config.timeout
        self.logger = logging.getLogger(__name__)
    
    def replace_variables(self, template_str, variables_dict):
        """Replace variables in template"""
        result = template_str
        for key, value in variables_dict.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def markdown_to_html(self, markdown_content):
        """Convert Markdown to HTML"""
        html = markdown.markdown(markdown_content)
        return f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ background-color: #f4f4f4; padding: 2px 6px; }}
                </style>
            </head>
            <body>{html}</body>
        </html>
        """
    
    def send_email(self, recipients, subject, content, cc=None, bcc=None, is_markdown=True):
        """Send email"""
        start_time = time.time()
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            text_part = MIMEText(content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            if is_markdown:
                html_content = self.markdown_to_html(content)
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            
            server.login(self.sender_email, self.sender_password)
            
            all_recipients = recipients.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            server.sendmail(self.sender_email, all_recipients, msg.as_string())
            server.quit()
            
            duration = int(time.time() - start_time)
            self.logger.info(f'Email sent to {len(recipients)} recipients')
            
            return {
                'success': True,
                'message': f'Email sent to {len(recipients)} recipients',
                'duration': duration,
                'timestamp': datetime.utcnow()
            }
        
        except smtplib.SMTPAuthenticationError as e:
            duration = int(time.time() - start_time)
            return {'success': False, 'message': 'SMTP authentication failed', 'duration': duration}
        
        except Exception as e:
            duration = int(time.time() - start_time)
            return {'success': False, 'message': f'Email sending failed: {str(e)}', 'duration': duration}
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            
            server.login(self.sender_email, self.sender_password)
            server.quit()
            
            return {'success': True, 'message': 'SMTP connection successful'}
        
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}