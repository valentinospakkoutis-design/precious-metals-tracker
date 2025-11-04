#!/bin/bash
# deploy.sh - Production deployment script for Financial Security API

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Financial Security API - Production Deployment${NC}"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Configuration
APP_DIR="/opt/financial-api"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="financial-api"
BACKUP_DIR="/var/backups/financial-api"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Step 1: Backup current version
echo -e "${YELLOW}📦 Step 1: Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
if [ -d "$APP_DIR" ]; then
    tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$APP_DIR" . || {
        echo -e "${RED}❌ Backup failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Backup created: backup_$TIMESTAMP.tar.gz${NC}"
else
    echo -e "${YELLOW}⚠️  No existing installation found${NC}"
fi
echo ""

# Step 2: Pull latest code
echo -e "${YELLOW}📥 Step 2: Pulling latest code...${NC}"
cd "$APP_DIR" || exit 1
git fetch origin
git reset --hard origin/main || {
    echo -e "${RED}❌ Git pull failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 3: Update virtual environment
echo -e "${YELLOW}🐍 Step 3: Updating Python dependencies...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt --upgrade || {
    echo -e "${RED}❌ Dependency installation failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Dependencies updated${NC}"
echo ""

# Step 4: Run database migrations (when implemented)
echo -e "${YELLOW}🗄️  Step 4: Running database migrations...${NC}"
# Uncomment when you implement migrations:
# alembic upgrade head || {
#     echo -e "${RED}❌ Database migration failed${NC}"
#     exit 1
# }
echo -e "${YELLOW}⚠️  Migrations not implemented yet (skipping)${NC}"
echo ""

# Step 5: Run tests
echo -e "${YELLOW}🧪 Step 5: Running tests...${NC}"
export TESTING=true
pytest || {
    echo -e "${RED}❌ Tests failed - deployment aborted${NC}"
    echo -e "${YELLOW}💡 Rolling back...${NC}"
    # Rollback to backup
    tar -xzf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$APP_DIR"
    exit 1
}
unset TESTING
echo -e "${GREEN}✅ All tests passed${NC}"
echo ""

# Step 6: Check environment variables
echo -e "${YELLOW}🔐 Step 6: Validating environment variables...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Check critical variables
REQUIRED_VARS=(
    "SECRET_KEY"
    "DATABASE_URL"
    "REDIS_HOST"
)

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" "$APP_DIR/.env"; then
        echo -e "${RED}❌ Missing required variable: $var${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Environment variables validated${NC}"
echo ""

# Step 7: Restart services
echo -e "${YELLOW}🔄 Step 7: Restarting services...${NC}"

# Restart PostgreSQL
systemctl restart postgresql || echo -e "${YELLOW}⚠️  PostgreSQL restart failed${NC}"

# Restart Redis
systemctl restart redis || echo -e "${YELLOW}⚠️  Redis restart failed${NC}"

# Restart application
systemctl restart "$SERVICE_NAME" || {
    echo -e "${RED}❌ Service restart failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Services restarted${NC}"
echo ""

# Step 8: Wait for application to start
echo -e "${YELLOW}⏳ Step 8: Waiting for application to start...${NC}"
sleep 10
echo ""

# Step 9: Health check
echo -e "${YELLOW}🏥 Step 9: Running health checks...${NC}"

# Check if service is running
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${RED}❌ Service is not running${NC}"
    journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    exit 1
fi

# HTTP health check
HEALTH_URL="http://localhost:8000/api/v1/health"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Health check failed (HTTP $HTTP_CODE)${NC}"
    journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    exit 1
fi
echo ""

# Step 10: Verify critical endpoints
echo -e "${YELLOW}🔍 Step 10: Verifying critical endpoints...${NC}"

ENDPOINTS=(
    "/api/v1/health"
    "/docs"
    "/api/v1/auth/register"
)

for endpoint in "${ENDPOINTS[@]}"; do
    URL="http://localhost:8000$endpoint"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
    
    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 307 ]; then
        echo -e "  ${GREEN}✅${NC} $endpoint (HTTP $HTTP_CODE)"
    else
        echo -e "  ${RED}❌${NC} $endpoint (HTTP $HTTP_CODE)"
    fi
done
echo ""

# Step 11: Cleanup old backups (keep last 10)
echo -e "${YELLOW}🧹 Step 11: Cleaning up old backups...${NC}"
cd "$BACKUP_DIR"
ls -t backup_*.tar.gz | tail -n +11 | xargs -r rm
BACKUP_COUNT=$(ls -1 backup_*.tar.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Keeping $BACKUP_COUNT most recent backups${NC}"
echo ""

# Step 12: Display status
echo -e "${GREEN}=================================================="
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "==================================================${NC}"
echo ""
echo "Service Status:"
systemctl status "$SERVICE_NAME" --no-pager -l | head -n 10
echo ""
echo "Recent Logs:"
journalctl -u "$SERVICE_NAME" -n 20 --no-pager
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "Useful commands:"
echo "  - View logs: journalctl -u $SERVICE_NAME -f"
echo "  - Restart service: systemctl restart $SERVICE_NAME"
echo "  - Check status: systemctl status $SERVICE_NAME"
echo "  - Rollback: ./rollback.sh $TIMESTAMP"
echo ""
