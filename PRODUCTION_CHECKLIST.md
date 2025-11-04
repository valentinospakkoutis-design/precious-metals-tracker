"""
Production Preparation Checklist
Complete guide for deploying the Financial Security API
"""

# PRODUCTION CHECKLIST - Financial Security API

## ✅ 1. Security Configuration

### 1.1 Environment Variables (CRITICAL)
- [ ] Generate secure SECRET_KEY (min 256 bits)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Set ALLOWED_ORIGINS for CORS
- [ ] Configure DATABASE_URL (PostgreSQL)
- [ ] Configure REDIS_URL
- [ ] Set SMTP credentials for email alerts
- [ ] Review all .env.example variables

### 1.2 Authentication Settings
- [ ] Verify ACCESS_TOKEN_EXPIRE_MINUTES (default: 15)
- [ ] Verify REFRESH_TOKEN_EXPIRE_DAYS (default: 7)
- [ ] Set account lockout threshold (default: 5 attempts)
- [ ] Set lockout duration (default: 1 hour)
- [ ] Review 2FA backup code count (default: 10)

### 1.3 Rate Limiting
- [ ] Configure rate limits per endpoint:
  - Login: 5/min
  - Register: 3/min
  - 2FA: 10/min
  - Portfolio: 60/min
  - Predictions: 20/min
- [ ] Test rate limiting with load tests
- [ ] Configure Redis for distributed rate limiting

---

## ✅ 2. Database Setup

### 2.1 PostgreSQL
- [ ] Install PostgreSQL 15+
- [ ] Create production database
  ```sql
  CREATE DATABASE financial_api_prod;
  CREATE USER api_user WITH PASSWORD 'secure_password';
  GRANT ALL PRIVILEGES ON DATABASE financial_api_prod TO api_user;
  ```
- [ ] Run migrations (when implemented)
- [ ] Set up automated backups (daily)
- [ ] Configure connection pooling (max 20 connections)
- [ ] Enable SSL connections

### 2.2 Redis
- [ ] Install Redis 7.0+
- [ ] Configure persistence (AOF + RDB)
  ```
  appendonly yes
  save 900 1
  save 300 10
  save 60 10000
  ```
- [ ] Set maxmemory policy: `allkeys-lru`
- [ ] Enable password authentication
- [ ] Configure master-slave replication (optional)
- [ ] Set up automated backups

### 2.3 Data Migration
- [ ] Export test data (if needed)
- [ ] Migrate users from in-memory to PostgreSQL
- [ ] Verify 2FA secrets migrated correctly
- [ ] Test backup/restore procedures

---

## ✅ 3. Infrastructure & Deployment

### 3.1 Server Requirements
- [ ] Python 3.11+ installed
- [ ] Minimum 2GB RAM
- [ ] 20GB SSD storage
- [ ] Ubuntu 22.04 LTS or similar

### 3.2 Web Server Setup
- [ ] Install Nginx or Apache
- [ ] Configure reverse proxy
  ```nginx
  server {
      listen 443 ssl http2;
      server_name api.yourdomain.com;
      
      ssl_certificate /path/to/cert.pem;
      ssl_certificate_key /path/to/key.pem;
      
      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```
- [ ] Enable HTTP/2
- [ ] Configure request size limits (10MB max)
- [ ] Set up rate limiting at proxy level

### 3.3 SSL/TLS Configuration
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Enable HTTPS only (redirect HTTP → HTTPS)
- [ ] Configure TLS 1.2+ only
- [ ] Enable HSTS headers
- [ ] Test SSL configuration: https://www.ssllabs.com/ssltest/

### 3.4 Process Management
- [ ] Install systemd service
  ```ini
  [Unit]
  Description=Financial Security API
  After=network.target postgresql.service redis.service
  
  [Service]
  User=apiuser
  WorkingDirectory=/opt/financial-api
  Environment="PATH=/opt/financial-api/venv/bin"
  ExecStart=/opt/financial-api/venv/bin/uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
  Restart=always
  
  [Install]
  WantedBy=multi-user.target
  ```
- [ ] Enable service auto-start
- [ ] Configure log rotation

---

## ✅ 4. Security Hardening

### 4.1 Firewall Configuration
- [ ] Enable UFW or iptables
- [ ] Allow only necessary ports (80, 443, SSH)
- [ ] Block direct access to 8000, 5432, 6379
- [ ] Configure fail2ban for SSH

### 4.2 Application Security
- [ ] Remove debug mode (DEBUG=False)
- [ ] Disable /docs and /redoc in production
- [ ] Enable CSRF protection (already implemented ✅)
- [ ] Review CORS allowed origins (whitelist only)
- [ ] Verify all inputs validated
- [ ] Test SQL injection resistance
- [ ] Test XSS resistance

### 4.3 Secrets Management
- [ ] Move all secrets to environment variables
- [ ] Use secret management service (AWS Secrets Manager, Vault)
- [ ] Rotate database passwords quarterly
- [ ] Rotate JWT SECRET_KEY annually
- [ ] Never commit .env to Git

### 4.4 Logging & Monitoring
- [ ] Configure structured logging (JSON format)
- [ ] Set log retention policy (90 days)
- [ ] Enable security event logging (already implemented ✅)
- [ ] Set up log aggregation (ELK Stack, CloudWatch)
- [ ] Configure alerts for:
  - Multiple failed logins
  - Account lockouts
  - Suspicious login patterns
  - High error rates
  - Service downtime

---

## ✅ 5. Performance Optimization

### 5.1 Application
- [ ] Enable production ASGI server (Gunicorn + Uvicorn)
- [ ] Configure worker count (CPU cores × 2 + 1)
- [ ] Enable response compression (gzip)
- [ ] Implement database query optimization
- [ ] Add caching layer (Redis already integrated ✅)
- [ ] Set up CDN for static assets

### 5.2 Database
- [ ] Create indexes on frequently queried fields
  ```sql
  CREATE INDEX idx_users_email ON users(email);
  CREATE INDEX idx_tokens_user_id ON revoked_tokens(user_id);
  ```
- [ ] Enable query result caching
- [ ] Configure connection pooling
- [ ] Run VACUUM ANALYZE regularly

### 5.3 Load Testing
- [ ] Test with 100 concurrent users
- [ ] Test with 1000 requests/second
- [ ] Identify bottlenecks
- [ ] Test failover scenarios
- [ ] Verify auto-scaling works

---

## ✅ 6. Email Configuration

### 6.1 SMTP Setup
- [ ] Configure SMTP server (Gmail, SendGrid, AWS SES)
- [ ] Set FROM email address
- [ ] Configure DKIM/SPF/DMARC
- [ ] Test email delivery
- [ ] Set up email templates
- [ ] Configure rate limits (avoid spam)

### 6.2 Email Alerts (already implemented ✅)
- [ ] Test account lockout emails
- [ ] Test suspicious login alerts
- [ ] Test 2FA notifications
- [ ] Test password change alerts
- [ ] Verify unsubscribe mechanism (future)

---

## ✅ 7. Testing

### 7.1 Unit Tests
- [ ] Run all unit tests: `pytest`
- [ ] Achieve >90% code coverage
- [ ] Test all security features
- [ ] Test all API endpoints

### 7.2 Integration Tests
- [ ] Test complete user registration flow
- [ ] Test complete 2FA enrollment flow
- [ ] Test login with wrong password 6 times (lockout)
- [ ] Test CSRF protection
- [ ] Test rate limiting
- [ ] Test token refresh flow

### 7.3 Security Tests
- [ ] Run OWASP ZAP scan
- [ ] Test for common vulnerabilities:
  - SQL Injection
  - XSS
  - CSRF (already protected ✅)
  - Path traversal
  - Command injection
- [ ] Test rate limiting bypass attempts
- [ ] Test JWT token manipulation
- [ ] Test 2FA bypass attempts

### 7.4 Load Tests
- [ ] Use tools: Locust, Apache JMeter, or k6
- [ ] Test sustained load (100 RPS for 1 hour)
- [ ] Test spike load (1000 RPS for 5 minutes)
- [ ] Monitor resource usage (CPU, RAM, disk)

---

## ✅ 8. Monitoring & Observability

### 8.1 Health Checks
- [ ] Implement /health endpoint (already exists ✅)
- [ ] Add /ready endpoint (checks DB, Redis)
- [ ] Configure uptime monitoring (Pingdom, UptimeRobot)
- [ ] Set up alerting (PagerDuty, Opsgenie)

### 8.2 Metrics
- [ ] Track request rate
- [ ] Track response times (p50, p95, p99)
- [ ] Track error rates (4xx, 5xx)
- [ ] Track database connection pool usage
- [ ] Track Redis memory usage
- [ ] Track login success/failure rates

### 8.3 Application Performance Monitoring
- [ ] Install APM tool (New Relic, Datadog, Sentry)
- [ ] Track slow endpoints
- [ ] Track slow database queries
- [ ] Set up error tracking
- [ ] Configure performance budgets

---

## ✅ 9. Backup & Disaster Recovery

### 9.1 Backup Strategy
- [ ] Automated daily PostgreSQL backups
- [ ] Automated daily Redis backups
- [ ] Store backups offsite (S3, GCS)
- [ ] Retain backups for 30 days
- [ ] Test backup restoration quarterly

### 9.2 Disaster Recovery Plan
- [ ] Document recovery procedures
- [ ] Test failover to backup server
- [ ] Set RTO (Recovery Time Objective): 4 hours
- [ ] Set RPO (Recovery Point Objective): 24 hours
- [ ] Maintain runbook for common issues

---

## ✅ 10. Compliance & Legal

### 10.1 Data Protection
- [ ] Review GDPR compliance (if EU users)
- [ ] Implement data deletion API
- [ ] Add privacy policy
- [ ] Add terms of service
- [ ] Implement data export feature
- [ ] Log all access to PII

### 10.2 Security Compliance
- [ ] Document security measures (SECURITY_AUDIT.md ✅)
- [ ] Complete penetration testing
- [ ] Obtain security certification (SOC 2, ISO 27001)
- [ ] Review third-party dependencies
- [ ] Scan for vulnerable dependencies: `pip-audit`

---

## ✅ 11. Documentation

### 11.1 API Documentation
- [ ] Review Swagger UI (/docs) ✅
- [ ] Add API usage examples
- [ ] Document rate limits
- [ ] Document error codes
- [ ] Create Postman collection ✅

### 11.2 Operational Documentation
- [ ] Write deployment guide
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Document backup/restore procedures
- [ ] Create incident response playbook

---

## ✅ 12. Pre-Launch Checklist

### Final Checks (DO THIS LAST)
- [ ] All tests passing ✅
- [ ] Code review completed
- [ ] Security audit completed
- [ ] Load testing passed
- [ ] Backup/restore tested
- [ ] Monitoring configured
- [ ] Alerts configured
- [ ] On-call rotation set up
- [ ] Rollback plan documented
- [ ] Launch announcement ready

---

## Quick Deploy Script

```bash
#!/bin/bash
# deploy.sh - Quick production deployment

set -e  # Exit on error

echo "🚀 Deploying Financial Security API..."

# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt --upgrade

# 4. Run database migrations (when implemented)
# alembic upgrade head

# 5. Run tests
pytest

# 6. Restart service
sudo systemctl restart financial-api

# 7. Check health
sleep 5
curl -f http://localhost:8000/api/v1/health || exit 1

echo "✅ Deployment successful!"
```

---

## Emergency Rollback

```bash
#!/bin/bash
# rollback.sh - Emergency rollback

set -e

echo "🔄 Rolling back to previous version..."

# 1. Revert to previous commit
git reset --hard HEAD~1

# 2. Restart service
sudo systemctl restart financial-api

# 3. Verify health
sleep 5
curl -f http://localhost:8000/api/v1/health || exit 1

echo "✅ Rollback successful!"
```

---

## Support Contacts

- **Technical Lead**: [Your Name]
- **On-Call**: [PagerDuty/Phone]
- **Email**: ops@yourdomain.com
- **Status Page**: status.yourdomain.com

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: READY FOR PRODUCTION ✅
