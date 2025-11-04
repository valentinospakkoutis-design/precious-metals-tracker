# Production Deployment Guide

## Prerequisites

### 1. Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- 2+ CPU cores
- 4GB+ RAM
- 20GB+ SSD storage
- Public IP address
- Domain name pointed to server

### 2. Software Requirements
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y

# Install Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
```

## Deployment Steps

### Step 1: Clone Repository
```bash
cd /var/www
sudo git clone <your-repo-url> financial-app
cd financial-app
sudo chown -R $USER:$USER /var/www/financial-app
```

### Step 2: Setup Python Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env

# Generate secret keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Setup PostgreSQL
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE financial_db;
CREATE USER financial_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE financial_db TO financial_user;
\q
```

### Step 5: Setup Redis
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Set password (find and uncomment):
# requirepass your-redis-password

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Step 6: Run Database Migrations
```bash
# If using Alembic
alembic upgrade head

# Or run your migration script
python backend/database/migrations/init_db.py
```

### Step 7: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/financial-app
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/financial-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: Setup SSL with Let's Encrypt
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow prompts. Certbot will:
- Verify domain ownership
- Generate SSL certificates
- Auto-configure Nginx for HTTPS
- Setup auto-renewal

Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

### Step 9: Create Systemd Service
```bash
sudo nano /etc/systemd/system/financial-app.service
```

```ini
[Unit]
Description=Financial Prediction API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/financial-app
Environment="PATH=/var/www/financial-app/venv/bin"
EnvironmentFile=/var/www/financial-app/.env
ExecStart=/var/www/financial-app/venv/bin/uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable financial-app
sudo systemctl start financial-app
sudo systemctl status financial-app
```

### Step 10: Setup Firewall
```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### Step 11: Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/financial-app
```

```
/var/www/financial-app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 www-data www-data
}
```

### Step 12: Setup Monitoring (Optional)
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Setup Sentry for error tracking
# Add SENTRY_DSN to .env file
```

## Security Checklist

- [ ] All secrets in .env (not in code)
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall configured (only 22, 80, 443 open)
- [ ] PostgreSQL password authentication
- [ ] Redis password set
- [ ] CORS configured for your domain only
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] Strong SECRET_KEY (32+ bytes)
- [ ] Regular backups configured
- [ ] Log rotation enabled
- [ ] Security headers in Nginx
- [ ] Account lockout enabled
- [ ] Device fingerprinting enabled

## Post-Deployment

### Verify Deployment
```bash
# Check service status
sudo systemctl status financial-app

# Check logs
sudo journalctl -u financial-app -f

# Test endpoints
curl https://yourdomain.com/api/v1/health
curl https://yourdomain.com/docs
```

### Setup Backups
```bash
# Create backup script
nano ~/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/var/backups/financial-app
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U financial_user financial_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup Redis
redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
```

```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /home/youruser/backup.sh
```

### Monitor Application
```bash
# View real-time logs
tail -f /var/www/financial-app/logs/app.log
tail -f /var/www/financial-app/logs/security.log

# Monitor system resources
htop

# Check nginx access logs
sudo tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Service won't start
```bash
# Check service logs
sudo journalctl -u financial-app -n 50

# Check Python errors
python backend/api/main.py

# Check permissions
ls -la /var/www/financial-app
```

### Database connection issues
```bash
# Test PostgreSQL connection
psql -U financial_user -d financial_db -h localhost

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Redis connection issues
```bash
# Test Redis
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

## Maintenance

### Update Application
```bash
cd /var/www/financial-app
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart financial-app
```

### Renew SSL Certificate
```bash
# Auto-renewal should work, but manual:
sudo certbot renew
sudo systemctl reload nginx
```

### Scale Up (Multiple Workers)
Edit `/etc/systemd/system/financial-app.service`:
```ini
ExecStart=/var/www/financial-app/venv/bin/uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --workers 8
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart financial-app
```

## Performance Optimization

### Enable Nginx Caching
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api/v1/price {
    proxy_cache api_cache;
    proxy_cache_valid 200 1m;
    proxy_pass http://127.0.0.1:8000;
}
```

### Enable Gzip Compression
```nginx
gzip on;
gzip_types application/json text/plain text/css application/javascript;
gzip_min_length 1000;
```

## Security Headers (Nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

✅ **Your application is now production-ready!**
