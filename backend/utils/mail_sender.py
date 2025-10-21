import smtplib
import logging
from datetime import datetime
import re
from markdown import markdown

logger = logging.getLogger(__name__)

class MailSender:
    def __init__(self, smtp_config):
        """Initialize mail sender with SMTP configuration"""
        self.smtp_server = smtp_config.smtp_server
        self.smtp_port = smtp_config.smtp_port
        self.sender_email = smtp_config.sender_email
        self.sender_password = smtp_config.sender_password
        self.use_tls = smtp_config.use_tls
        self.timeout = getattr(smtp_config, 'timeout', 30)
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            logger.info(f'Testing SMTP connection to {self.smtp_server}:{self.smtp_port}')
            
            # 创建SMTP连接
            if self.use_tls and self.smtp_port == 465:
                # 使用 SMTP_SSL 用于端口 465
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            elif self.use_tls and self.smtp_port == 587:
                # 使用 SMTP + STARTTLS 用于端口 587
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            else:
                # 普通 SMTP
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
            
            # 登录
            server.login(self.sender_email, self.sender_password)
            logger.info('SMTP login successful')
            
            # 关闭连接
            server.quit()
            
            logger.info('SMTP connection test passed')
            return {
                'success': True,
                'message': 'SMTP connection successful'
            }
        
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f'SMTP authentication failed: {str(e)}')
            return {
                'success': False,
                'message': f'Authentication failed: Please check your email and password'
            }
        
        except smtplib.SMTPException as e:
            logger.error(f'SMTP error: {str(e)}')
            return {
                'success': False,
                'message': f'SMTP error: {str(e)}'
            }
        
        except Exception as e:
            logger.error(f'Connection error: {str(e)}')
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }
    
    def send_email(self, recipients, subject, content, cc=None, bcc=None, is_markdown=False):
        """Send email"""
        try:
            logger.info(f'Preparing to send email to {recipients}')
            
            # 转换Markdown为HTML（如果需要）
            if is_markdown:
                content = markdown(content)
            
            # 创建SMTP连接
            if self.use_tls and self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=self.timeout)
            elif self.use_tls and self.smtp_port == 587:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
                server.starttls()
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout)
            
            # 登录
            server.login(self.sender_email, self.sender_password)
            logger.info('SMTP login successful for sending')
            
            # 准备邮件内容
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # 添加文本和HTML版本
            msg.attach(MIMEText(content, 'html' if is_markdown else 'plain'))
            
            # 发送邮件
            all_recipients = recipients + (cc or []) + (bcc or [])
            server.sendmail(self.sender_email, all_recipients, msg.as_string())
            server.quit()
            
            logger.info(f'Email sent successfully to {recipients}')
            return {
                'success': True,
                'message': f'Email sent to {len(recipients)} recipients',
                'timestamp': datetime.utcnow().isoformat(),
                'duration': 0
            }
        
        except Exception as e:
            logger.error(f'Error sending email: {str(e)}')
            return {
                'success': False,
                'message': f'Error sending email: {str(e)}'
            }
    
    def replace_variables(self, text, variables):
        """Replace variables in template"""
        result = text
        for key, value in variables.items():
            result = result.replace(f'{{{{{key}}}}}', str(value))
        return result