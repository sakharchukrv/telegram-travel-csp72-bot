#!/bin/bash

# Deployment script for Telegram Bot fixes
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${YELLOW}📥 Step 1: Pulling latest changes from GitHub...${NC}"
git pull origin master
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to pull from GitHub${NC}"
    echo "Trying alternative method..."
    
    # Backup current files
    mkdir -p /tmp/bot_backup
    cp -r bot /tmp/bot_backup/
    
    # Download specific files
    echo "Downloading updated files..."
    wget -q -O bot/utils/excel_generator.py "https://raw.githubusercontent.com/sakharchukrv/telegram-travel-csp72-bot/master/bot/utils/excel_generator.py"
    wget -q -O bot/handlers/drafts.py "https://raw.githubusercontent.com/sakharchukrv/telegram-travel-csp72-bot/master/bot/handlers/drafts.py"
    wget -q -O bot/handlers/application.py "https://raw.githubusercontent.com/sakharchukrv/telegram-travel-csp72-bot/master/bot/handlers/application.py"
    
    echo -e "${GREEN}✅ Files downloaded${NC}"
fi

echo ""
echo -e "${YELLOW}🛑 Step 2: Stopping current bot...${NC}"
docker-compose down
echo -e "${GREEN}✅ Bot stopped${NC}"

echo ""
echo -e "${YELLOW}🏗️  Step 3: Rebuilding Docker image...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Image rebuilt${NC}"

echo ""
echo -e "${YELLOW}🚀 Step 4: Starting bot...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Bot started${NC}"

echo ""
echo -e "${YELLOW}⏳ Waiting for bot to initialize...${NC}"
sleep 5

echo ""
echo -e "${YELLOW}📊 Step 5: Checking bot status...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Bot is running!${NC}"
else
    echo -e "${RED}❌ Bot is not running${NC}"
    echo "Showing recent logs:"
    docker-compose logs --tail=50 bot
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "📝 Next steps:"
echo "  1. Check logs: docker-compose logs -f bot"
echo "  2. Test the bot in Telegram"
echo "  3. Verify email functionality"
echo ""
echo "🧪 Testing checklist:"
echo "  ✓ Submit a new application"
echo "  ✓ Save a draft"
echo "  ✓ Load and continue a draft"
echo "  ✓ Delete a draft"
echo "  ✓ Check email received"
echo ""
echo "📊 View logs now? (y/n)"
read -t 10 -n 1 answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo ""
    echo "Showing logs (Ctrl+C to exit):"
    docker-compose logs -f bot
fi
