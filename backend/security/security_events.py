"""
Security Event Integration
Integrates email alerts with security logging
"""

import logging
from typing import Optional
from datetime import datetime

# Try to import email alerts (optional dependency)
try:
    from security.email_alerts import SecurityEmailer
    EMAIL_ALERTS_ENABLED = True
except ImportError:
    EMAIL_ALERTS_ENABLED = False
    SecurityEmailer = None

logger = logging.getLogger(__name__)


class SecurityEventHandler:
    """
    Centralized security event handler
    Integrates logging and email alerts
    """
    
    def __init__(self):
        """Initialize event handler"""
        self.emailer = None
        
        # Try to initialize email alerts
        if EMAIL_ALERTS_ENABLED:
            try:
                self.emailer = SecurityEmailer()
                logger.info("✅ Email alerts enabled")
            except Exception as e:
                logger.warning(f"⚠️  Email alerts disabled: {e}")
                self.emailer = None
        else:
            logger.warning("⚠️  Email alerts module not available")
    
    def account_locked(self, email: str, ip_address: str, attempts: int):
        """
        Handle account lockout event
        
        Args:
            email: User's email
            ip_address: IP address of failed attempts
            attempts: Number of failed attempts
        """
        # Log the event
        logger.warning(
            f"SECURITY: Account locked - Email: {email}, IP: {ip_address}, Attempts: {attempts}",
            extra={
                "event_type": "account_locked",
                "email": email,
                "ip_address": ip_address,
                "attempts": attempts,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send email alert
        if self.emailer:
            try:
                self.emailer.send_account_lockout_alert(
                    email=email,
                    ip_address=ip_address,
                    failed_attempts=attempts
                )
                logger.info(f"📧 Lockout alert sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send lockout email to {email}: {e}")
    
    def suspicious_login(
        self,
        email: str,
        ip_address: str,
        user_agent: str,
        reason: str = "Unknown device"
    ):
        """
        Handle suspicious login attempt
        
        Args:
            email: User's email
            ip_address: IP address of attempt
            user_agent: Browser/device user agent
            reason: Reason for suspicion
        """
        # Log the event
        logger.warning(
            f"SECURITY: Suspicious login - Email: {email}, IP: {ip_address}, Reason: {reason}",
            extra={
                "event_type": "suspicious_login",
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send email alert
        if self.emailer:
            try:
                self.emailer.send_suspicious_login_alert(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.now()
                )
                logger.info(f"📧 Suspicious login alert sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send suspicious login email to {email}: {e}")
    
    def two_factor_enabled(self, email: str):
        """
        Handle 2FA enabled event
        
        Args:
            email: User's email
        """
        # Log the event
        logger.info(
            f"SECURITY: 2FA enabled - Email: {email}",
            extra={
                "event_type": "2fa_enabled",
                "email": email,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send email notification
        if self.emailer:
            try:
                self.emailer.send_2fa_enabled_notification(email)
                logger.info(f"📧 2FA enabled notification sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send 2FA notification to {email}: {e}")
    
    def two_factor_disabled(self, email: str):
        """
        Handle 2FA disabled event
        
        Args:
            email: User's email
        """
        # Log the event
        logger.warning(
            f"SECURITY: 2FA disabled - Email: {email}",
            extra={
                "event_type": "2fa_disabled",
                "email": email,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send email notification
        if self.emailer:
            try:
                self.emailer.send_2fa_disabled_notification(email)
                logger.info(f"📧 2FA disabled notification sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send 2FA disabled notification to {email}: {e}")
    
    def password_changed(self, email: str, ip_address: str):
        """
        Handle password change event
        
        Args:
            email: User's email
            ip_address: IP address of change
        """
        # Log the event
        logger.info(
            f"SECURITY: Password changed - Email: {email}, IP: {ip_address}",
            extra={
                "event_type": "password_changed",
                "email": email,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Send email notification
        if self.emailer:
            try:
                self.emailer.send_password_change_notification(email)
                logger.info(f"📧 Password change notification sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send password change notification to {email}: {e}")
    
    def successful_login(self, email: str, ip_address: str, user_agent: str):
        """
        Handle successful login (for logging only, no email)
        
        Args:
            email: User's email
            ip_address: IP address
            user_agent: Browser/device user agent
        """
        logger.info(
            f"LOGIN: Successful - Email: {email}, IP: {ip_address}",
            extra={
                "event_type": "successful_login",
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def failed_login(self, email: str, ip_address: str, attempts: int):
        """
        Handle failed login attempt
        
        Args:
            email: User's email
            ip_address: IP address
            attempts: Current attempt count
        """
        logger.warning(
            f"LOGIN: Failed - Email: {email}, IP: {ip_address}, Attempts: {attempts}",
            extra={
                "event_type": "failed_login",
                "email": email,
                "ip_address": ip_address,
                "attempts": attempts,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def token_revoked(self, email: str, reason: str = "Logout"):
        """
        Handle token revocation
        
        Args:
            email: User's email
            reason: Reason for revocation
        """
        logger.info(
            f"SECURITY: Token revoked - Email: {email}, Reason: {reason}",
            extra={
                "event_type": "token_revoked",
                "email": email,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        )


# Global event handler instance
security_events = SecurityEventHandler()


# Convenience functions for easy import
def notify_account_locked(email: str, ip_address: str, attempts: int):
    """Notify about account lockout"""
    security_events.account_locked(email, ip_address, attempts)


def notify_suspicious_login(email: str, ip_address: str, user_agent: str, reason: str = "Unknown device"):
    """Notify about suspicious login"""
    security_events.suspicious_login(email, ip_address, user_agent, reason)


def notify_2fa_enabled(email: str):
    """Notify about 2FA enabled"""
    security_events.two_factor_enabled(email)


def notify_2fa_disabled(email: str):
    """Notify about 2FA disabled"""
    security_events.two_factor_disabled(email)


def notify_password_changed(email: str, ip_address: str):
    """Notify about password change"""
    security_events.password_changed(email, ip_address)


def log_successful_login(email: str, ip_address: str, user_agent: str):
    """Log successful login"""
    security_events.successful_login(email, ip_address, user_agent)


def log_failed_login(email: str, ip_address: str, attempts: int):
    """Log failed login"""
    security_events.failed_login(email, ip_address, attempts)


def log_token_revoked(email: str, reason: str = "Logout"):
    """Log token revocation"""
    security_events.token_revoked(email, reason)


if __name__ == "__main__":
    """Test security event handler"""
    
    print("🧪 Testing Security Event Handler\n")
    
    # Test 1: Account lockout
    print("Test 1: Account Lockout")
    notify_account_locked("test@example.com", "192.168.1.100", 5)
    print("✅ Logged account lockout\n")
    
    # Test 2: Suspicious login
    print("Test 2: Suspicious Login")
    notify_suspicious_login(
        "test@example.com",
        "203.0.113.42",
        "Mozilla/5.0 (Unknown Device)",
        "Login from new country"
    )
    print("✅ Logged suspicious login\n")
    
    # Test 3: 2FA enabled
    print("Test 3: 2FA Enabled")
    notify_2fa_enabled("test@example.com")
    print("✅ Logged 2FA enabled\n")
    
    # Test 4: Successful login
    print("Test 4: Successful Login")
    log_successful_login("test@example.com", "192.168.1.100", "Chrome/119.0")
    print("✅ Logged successful login\n")
    
    # Test 5: Failed login
    print("Test 5: Failed Login")
    log_failed_login("test@example.com", "192.168.1.100", 3)
    print("✅ Logged failed login\n")
    
    print("✅ All security event tests completed!")
