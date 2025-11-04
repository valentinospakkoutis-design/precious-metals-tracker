#!/bin/bash
# rollback.sh - Emergency rollback script for Financial Security API

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}🔄 Financial Security API - EMERGENCY ROLLBACK${NC}"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo)${NC}"
    exit 1
fi

# Configuration
APP_DIR="/opt/financial-api"
BACKUP_DIR="/var/backups/financial-api"
SERVICE_NAME="financial-api"

# Get backup timestamp from argument or use latest
if [ -n "$1" ]; then
    BACKUP_FILE="$BACKUP_DIR/backup_$1.tar.gz"
else
    # Find most recent backup
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -n 1)
fi

# Verify backup exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

echo -e "${YELLOW}📦 Using backup: $(basename $BACKUP_FILE)${NC}"
echo ""

# Confirmation prompt
read -p "⚠️  Are you sure you want to rollback? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Rollback cancelled${NC}"
    exit 0
fi

# Step 1: Stop service
echo -e "${YELLOW}⏸️  Step 1: Stopping service...${NC}"
systemctl stop "$SERVICE_NAME" || {
    echo -e "${RED}❌ Failed to stop service${NC}"
    exit 1
}
echo -e "${GREEN}✅ Service stopped${NC}"
echo ""

# Step 2: Backup current state (just in case)
echo -e "${YELLOW}💾 Step 2: Creating emergency backup of current state...${NC}"
EMERGENCY_BACKUP="$BACKUP_DIR/emergency_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$EMERGENCY_BACKUP" -C "$APP_DIR" . || {
    echo -e "${RED}❌ Emergency backup failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ Emergency backup created: $(basename $EMERGENCY_BACKUP)${NC}"
echo ""

# Step 3: Remove current installation
echo -e "${YELLOW}🗑️  Step 3: Removing current installation...${NC}"
cd "$APP_DIR"
rm -rf ./* || {
    echo -e "${RED}❌ Failed to remove current installation${NC}"
    exit 1
}
echo -e "${GREEN}✅ Current installation removed${NC}"
echo ""

# Step 4: Restore from backup
echo -e "${YELLOW}📥 Step 4: Restoring from backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$APP_DIR" || {
    echo -e "${RED}❌ Restore failed${NC}"
    echo -e "${YELLOW}💡 Attempting to restore emergency backup...${NC}"
    tar -xzf "$EMERGENCY_BACKUP" -C "$APP_DIR"
    exit 1
}
echo -e "${GREEN}✅ Files restored${NC}"
echo ""

# Step 5: Restart service
echo -e "${YELLOW}🔄 Step 5: Restarting service...${NC}"
systemctl start "$SERVICE_NAME" || {
    echo -e "${RED}❌ Service restart failed${NC}"
    journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    exit 1
}
echo -e "${GREEN}✅ Service restarted${NC}"
echo ""

# Step 6: Wait for startup
echo -e "${YELLOW}⏳ Step 6: Waiting for service to start...${NC}"
sleep 10
echo ""

# Step 7: Health check
echo -e "${YELLOW}🏥 Step 7: Running health check...${NC}"

if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${RED}❌ Service is not running${NC}"
    journalctl -u "$SERVICE_NAME" -n 50 --no-pager
    exit 1
fi

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

# Success
echo -e "${GREEN}=================================================="
echo "✅ ROLLBACK SUCCESSFUL"
echo "==================================================${NC}"
echo ""
echo "Service Status:"
systemctl status "$SERVICE_NAME" --no-pager -l | head -n 10
echo ""
echo "Recent Logs:"
journalctl -u "$SERVICE_NAME" -n 20 --no-pager
echo ""
echo -e "${GREEN}🎉 Rollback completed successfully!${NC}"
echo ""
echo "Emergency backup saved at:"
echo "  $EMERGENCY_BACKUP"
echo ""
