#!/bin/bash
# ============================================
# MiPymesIA - VPS Deployment Script
# ============================================
# 
# This script should be run on the VPS after pushing code to GitHub
# Usage: bash deploy_on_vps.sh

set -e  # Exit on error

echo ""
echo "============================================"
echo "  MiPymesIA - VPS Deployment"
echo "============================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR=$(pwd)
SERVICE_NAME="mipymesia"  # Change this to your actual service name
BACKUP_DIR="$HOME/backups/mipymesia_$(date +%Y%m%d_%H%M%S)"

# Step 1: Create backup
echo -e "${BLUE}[1/7] Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"

if [ -f "users.db" ]; then
    cp users.db "$BACKUP_DIR/users.db"
    echo -e "${GREEN}✅ Database backed up to: $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  No database found, skipping backup${NC}"
fi

# Backup current code
cp -r . "$BACKUP_DIR/codigo" 2>/dev/null || true
echo -e "${GREEN}✅ Code backed up${NC}"

echo ""
echo "============================================"
echo ""

# Step 2: Stop the application
echo -e "${BLUE}[2/7] Stopping application...${NC}"

# Try systemctl first
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    sudo systemctl stop "$SERVICE_NAME"
    echo -e "${GREEN}✅ Service stopped${NC}"
elif pgrep -f "streamlit run main.py" > /dev/null; then
    # If running as process, kill it
    pkill -f "streamlit run main.py"
    echo -e "${GREEN}✅ Streamlit process stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Application not running${NC}"
fi

echo ""
echo "============================================"
echo ""

# Step 3: Pull latest code
echo -e "${BLUE}[3/7] Pulling latest code from GitHub...${NC}"

git fetch origin
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Code updated successfully${NC}"
else
    echo -e "${RED}❌ Failed to pull code from GitHub${NC}"
    echo "You may need to resolve conflicts manually"
    exit 1
fi

echo ""
echo "============================================"
echo ""

# Step 4: Activate virtual environment and update dependencies
echo -e "${BLUE}[4/7] Updating dependencies...${NC}"

# Find virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating new virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

pip install -r requirements.txt --upgrade

echo -e "${GREEN}✅ Dependencies updated${NC}"

echo ""
echo "============================================"
echo ""

# Step 5: Run database migrations
echo -e "${BLUE}[5/7] Running database migrations...${NC}"

python db_migrations.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migrations completed${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    echo "Check the error above and fix before continuing"
    exit 1
fi

echo ""
echo "============================================"
echo ""

# Step 6: Verify database
echo -e "${BLUE}[6/7] Verifying database...${NC}"

if [ -f "users.db" ]; then
    DB_SIZE=$(du -h users.db | cut -f1)
    echo -e "${GREEN}✅ Database exists (Size: $DB_SIZE)${NC}"
    
    # Check tables
    TABLES=$(sqlite3 users.db "SELECT name FROM sqlite_master WHERE type='table';" | wc -l)
    echo -e "${GREEN}✅ Database has $TABLES tables${NC}"
else
    echo -e "${RED}❌ Database not found!${NC}"
    exit 1
fi

echo ""
echo "============================================"
echo ""

# Step 7: Start the application
echo -e "${BLUE}[7/7] Starting application...${NC}"

if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    sudo systemctl start "$SERVICE_NAME"
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Service started successfully${NC}"
        
        # Show status
        echo ""
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
    else
        echo -e "${RED}❌ Service failed to start${NC}"
        echo "Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Systemd service not configured${NC}"
    echo "You may need to start the application manually"
    echo "Example: streamlit run main.py --server.port 8501"
fi

echo ""
echo "============================================"
echo -e "${GREEN}  DEPLOYMENT COMPLETE!${NC}"
echo "============================================"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Verification checklist:"
echo "  [ ] Application is running"
echo "  [ ] Users can log in"
echo "  [ ] New features are working"
echo "  [ ] No errors in logs"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "To check application status:"
echo "  sudo systemctl status $SERVICE_NAME"
echo ""
