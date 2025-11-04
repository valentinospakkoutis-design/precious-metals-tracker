"""
Security Event Logger
Dedicated logging for security-related events
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import os

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Security log file
SECURITY_LOG_FILE = LOGS_DIR / "security_events.log"
SECURITY_JSON_LOG = LOGS_DIR / "security_events.json"


class SecurityLogger:
    """
    Dedicated logger for security events
    
    Logs to both file and JSON for analysis
    """
    
    def __init__(self):
        # Setup file logger
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        # File handler for human-readable logs
        file_handler = logging.FileHandler(SECURITY_LOG_FILE)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(event_type)s] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler for immediate visibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
        console_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Track event counts for alerts
        self.event_counts = {}
        self.alert_thresholds = {
            "failed_login": 10,       # 10 failed logins
            "rate_limit": 20,         # 20 rate limit hits
            "invalid_token": 15,      # 15 invalid tokens
            "suspicious_input": 30,   # 30 suspicious inputs
            "csrf_failed": 5          # 5 CSRF failures
        }
    
    def _log_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_email: Optional[str] = None
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of event (failed_login, rate_limit, etc)
            severity: INFO, WARNING, ERROR, CRITICAL
            message: Human-readable message
            details: Additional event details
            ip_address: Client IP address
            user_email: User email if authenticated
        """
        # Create event record
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "ip_address": ip_address,
            "user_email": user_email,
            "details": details or {}
        }
        
        # Log to file
        extra = {"event_type": event_type}
        log_msg = f"{message}"
        if ip_address:
            log_msg += f" | IP: {ip_address}"
        if user_email:
            log_msg += f" | User: {user_email}"
        
        if severity == "INFO":
            self.logger.info(log_msg, extra=extra)
        elif severity == "WARNING":
            self.logger.warning(log_msg, extra=extra)
        elif severity == "ERROR":
            self.logger.error(log_msg, extra=extra)
        elif severity == "CRITICAL":
            self.logger.critical(log_msg, extra=extra)
        
        # Log to JSON file
        self._log_json(event)
        
        # Track counts and check thresholds
        self._check_alert_threshold(event_type)
    
    def _log_json(self, event: dict):
        """Append event to JSON log file"""
        try:
            with open(SECURITY_JSON_LOG, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")
    
    def _check_alert_threshold(self, event_type: str):
        """Check if event count exceeds alert threshold"""
        if event_type not in self.event_counts:
            self.event_counts[event_type] = 0
        
        self.event_counts[event_type] += 1
        
        if event_type in self.alert_thresholds:
            threshold = self.alert_thresholds[event_type]
            count = self.event_counts[event_type]
            
            if count >= threshold and count % threshold == 0:
                self.logger.critical(
                    f"ALERT: {event_type} threshold exceeded! "
                    f"Count: {count} (threshold: {threshold})",
                    extra={"event_type": "security_alert"}
                )
    
    # Convenience methods for common events
    
    def log_failed_login(
        self,
        email: str,
        ip_address: str,
        attempts_remaining: int,
        reason: str = "Invalid credentials"
    ):
        """Log failed login attempt"""
        self._log_event(
            event_type="failed_login",
            severity="WARNING",
            message=f"Failed login attempt for {email}",
            details={
                "reason": reason,
                "attempts_remaining": attempts_remaining
            },
            ip_address=ip_address,
            user_email=email
        )
    
    def log_account_locked(self, email: str, ip_address: str, duration_seconds: int):
        """Log account lockout"""
        self._log_event(
            event_type="account_locked",
            severity="ERROR",
            message=f"Account locked: {email}",
            details={"lock_duration": duration_seconds},
            ip_address=ip_address,
            user_email=email
        )
    
    def log_successful_login(self, email: str, ip_address: str):
        """Log successful login"""
        self._log_event(
            event_type="successful_login",
            severity="INFO",
            message=f"Successful login: {email}",
            ip_address=ip_address,
            user_email=email
        )
    
    def log_rate_limit_exceeded(
        self,
        endpoint: str,
        ip_address: str,
        limit: str,
        user_email: Optional[str] = None
    ):
        """Log rate limit violation"""
        self._log_event(
            event_type="rate_limit",
            severity="WARNING",
            message=f"Rate limit exceeded for {endpoint}",
            details={
                "endpoint": endpoint,
                "limit": limit
            },
            ip_address=ip_address,
            user_email=user_email
        )
    
    def log_invalid_token(self, ip_address: str, reason: str):
        """Log invalid JWT token attempt"""
        self._log_event(
            event_type="invalid_token",
            severity="WARNING",
            message=f"Invalid token: {reason}",
            details={"reason": reason},
            ip_address=ip_address
        )
    
    def log_revoked_token_use(self, ip_address: str, user_email: Optional[str] = None):
        """Log attempt to use revoked token"""
        self._log_event(
            event_type="revoked_token",
            severity="ERROR",
            message="Attempt to use revoked token",
            ip_address=ip_address,
            user_email=user_email
        )
    
    def log_csrf_failed(self, endpoint: str, ip_address: str):
        """Log CSRF validation failure"""
        self._log_event(
            event_type="csrf_failed",
            severity="ERROR",
            message=f"CSRF validation failed for {endpoint}",
            details={"endpoint": endpoint},
            ip_address=ip_address
        )
    
    def log_suspicious_input(
        self,
        input_type: str,
        value: str,
        ip_address: str,
        user_email: Optional[str] = None
    ):
        """Log suspicious input detection"""
        self._log_event(
            event_type="suspicious_input",
            severity="WARNING",
            message=f"Suspicious {input_type} detected",
            details={
                "input_type": input_type,
                "value": value[:100]  # Truncate for safety
            },
            ip_address=ip_address,
            user_email=user_email
        )
    
    def log_sql_injection_attempt(
        self,
        query: str,
        ip_address: str,
        user_email: Optional[str] = None
    ):
        """Log potential SQL injection attempt"""
        self._log_event(
            event_type="sql_injection",
            severity="CRITICAL",
            message="Potential SQL injection attempt detected",
            details={"query_fragment": query[:200]},
            ip_address=ip_address,
            user_email=user_email
        )
    
    def get_stats(self) -> dict:
        """Get event statistics"""
        return {
            "total_events": sum(self.event_counts.values()),
            "event_breakdown": self.event_counts.copy(),
            "alert_thresholds": self.alert_thresholds.copy(),
            "log_file": str(SECURITY_LOG_FILE),
            "json_log": str(SECURITY_JSON_LOG)
        }


# Global security logger instance
security_logger = SecurityLogger()


# Helper function to get client IP from request
def get_client_ip(request) -> str:
    """Extract client IP from request"""
    # Check X-Forwarded-For header (for proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"
