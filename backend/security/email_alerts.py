"""
Email Security Alerts
Send notifications for critical security events
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from typing import Optional, List
import os
import logging

logger = logging.getLogger(__name__)


class SecurityEmailer:
    """
    Send security alert emails
    
    Supports:
    - Account lockout notifications
    - Suspicious login alerts
    - Password change confirmations
    - 2FA setup/disable notifications
    - Admin security summaries
    """
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Initialize email service
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or self.smtp_user
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured - email alerts disabled")
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback
            
        Returns:
            True if sent successfully
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning(f"Email not sent (no SMTP config): {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            
            # Add text part
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    def send_account_locked_alert(
        self,
        email: str,
        lock_duration_minutes: int,
        ip_address: str
    ) -> bool:
        """
        Send account lockout notification
        
        Args:
            email: User's email
            lock_duration_minutes: How long account is locked
            ip_address: IP that triggered lockout
        """
        subject = "🔒 Security Alert: Account Locked"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #d32f2f;">🔒 Account Locked</h2>
                
                <p>Your account has been temporarily locked due to multiple failed login attempts.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Details:</strong></p>
                    <ul style="list-style: none; padding-left: 0;">
                        <li>📧 <strong>Email:</strong> {email}</li>
                        <li>🌐 <strong>IP Address:</strong> {ip_address}</li>
                        <li>⏰ <strong>Lock Duration:</strong> {lock_duration_minutes} minutes</li>
                        <li>🕐 <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
                    </ul>
                </div>
                
                <p><strong>What happened?</strong><br>
                After 5 failed login attempts, your account has been temporarily locked to prevent unauthorized access.</p>
                
                <p><strong>What should you do?</strong></p>
                <ul>
                    <li>✅ Wait {lock_duration_minutes} minutes, then try logging in again</li>
                    <li>✅ Make sure you're using the correct password</li>
                    <li>✅ If you forgot your password, use the "Forgot Password" option</li>
                    <li>⚠️ If you didn't attempt to login, change your password immediately</li>
                </ul>
                
                <p><strong>Need help?</strong><br>
                If you believe this is an error or need assistance, please contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated security alert. Do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        SECURITY ALERT: Account Locked
        
        Your account has been temporarily locked due to multiple failed login attempts.
        
        Details:
        - Email: {email}
        - IP Address: {ip_address}
        - Lock Duration: {lock_duration_minutes} minutes
        - Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
        
        Wait {lock_duration_minutes} minutes, then try logging in again.
        If you didn't attempt to login, change your password immediately.
        """
        
        return self._send_email(email, subject, html_body, text_body)
    
    def send_suspicious_login_alert(
        self,
        email: str,
        ip_address: str,
        location: Optional[str] = None,
        device: Optional[str] = None
    ) -> bool:
        """
        Send suspicious login attempt notification
        
        Args:
            email: User's email
            ip_address: Login IP address
            location: Geolocation (if available)
            device: Device info
        """
        subject = "⚠️ Security Alert: Suspicious Login Attempt"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #ff6f00;">⚠️ Suspicious Login Attempt Detected</h2>
                
                <p>We detected a login attempt from an unusual location or device.</p>
                
                <div style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff6f00; margin: 20px 0;">
                    <p><strong>Login Details:</strong></p>
                    <ul style="list-style: none; padding-left: 0;">
                        <li>📧 <strong>Email:</strong> {email}</li>
                        <li>🌐 <strong>IP Address:</strong> {ip_address}</li>
                        {f'<li>📍 <strong>Location:</strong> {location}</li>' if location else ''}
                        {f'<li>📱 <strong>Device:</strong> {device}</li>' if device else ''}
                        <li>🕐 <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
                    </ul>
                </div>
                
                <p><strong>Was this you?</strong></p>
                <ul>
                    <li>✅ If yes, you can safely ignore this email</li>
                    <li>❌ If no, <strong>change your password immediately</strong></li>
                </ul>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Recommended Actions:</strong></p>
                    <ul>
                        <li>Change your password</li>
                        <li>Enable Two-Factor Authentication (2FA)</li>
                        <li>Review recent account activity</li>
                        <li>Check for unauthorized access</li>
                    </ul>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated security alert. Do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_body)
    
    def send_password_changed_confirmation(self, email: str) -> bool:
        """Send password change confirmation"""
        subject = "✅ Password Changed Successfully"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #2e7d32;">✅ Password Changed</h2>
                
                <p>Your password was successfully changed.</p>
                
                <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Change Details:</strong></p>
                    <ul style="list-style: none; padding-left: 0;">
                        <li>📧 <strong>Email:</strong> {email}</li>
                        <li>🕐 <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</li>
                    </ul>
                </div>
                
                <p><strong>Did you make this change?</strong></p>
                <ul>
                    <li>✅ If yes, no further action needed</li>
                    <li>❌ If no, <strong>contact support immediately</strong></li>
                </ul>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    This is an automated security notification.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_body)
    
    def send_2fa_enabled_notification(self, email: str) -> bool:
        """Send 2FA enabled confirmation"""
        subject = "🔐 Two-Factor Authentication Enabled"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #2e7d32;">🔐 2FA Enabled</h2>
                
                <p>Two-Factor Authentication (2FA) has been successfully enabled for your account.</p>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>What this means:</strong></p>
                    <ul>
                        <li>✅ Your account is now more secure</li>
                        <li>✅ You'll need your authenticator app to login</li>
                        <li>✅ You received backup codes for account recovery</li>
                    </ul>
                </div>
                
                <p><strong>Important:</strong> Keep your backup codes in a safe place!</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    If you didn't enable 2FA, contact support immediately.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_body)
    
    def send_admin_security_summary(
        self,
        admin_email: str,
        stats: dict
    ) -> bool:
        """
        Send daily security summary to admin
        
        Args:
            admin_email: Admin email address
            stats: Security statistics
        """
        subject = f"📊 Security Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #1976d2;">📊 Daily Security Summary</h2>
                
                <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Key Metrics:</h3>
                    <ul>
                        <li>🔒 <strong>Account Lockouts:</strong> {stats.get('lockouts', 0)}</li>
                        <li>⚠️ <strong>Failed Login Attempts:</strong> {stats.get('failed_logins', 0)}</li>
                        <li>🚫 <strong>Rate Limit Violations:</strong> {stats.get('rate_limits', 0)}</li>
                        <li>🎫 <strong>Revoked Tokens:</strong> {stats.get('revoked_tokens', 0)}</li>
                        <li>🛡️ <strong>CSRF Blocks:</strong> {stats.get('csrf_blocks', 0)}</li>
                        <li>📝 <strong>Security Events:</strong> {stats.get('total_events', 0)}</li>
                    </ul>
                </div>
                
                <p><strong>Status:</strong> 
                    <span style="color: #2e7d32; font-weight: bold;">
                        All systems operational ✅
                    </span>
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    Automated security report. Review logs for details.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(admin_email, subject, html_body)


# Global instance
def get_security_emailer() -> SecurityEmailer:
    """Get security emailer instance"""
    return SecurityEmailer(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", 587)),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        from_email=os.getenv("FROM_EMAIL")
    )


# Testing
if __name__ == "__main__":
    emailer = get_security_emailer()
    
    # Test account lockout email
    print("Sending test email...")
    result = emailer.send_account_locked_alert(
        email="user@example.com",
        lock_duration_minutes=60,
        ip_address="192.168.1.100"
    )
    print(f"Email sent: {result}")
