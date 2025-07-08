#!/bin/bash

# Astrid Mart - Game Launcher Script
# Provides easy ways to start the game with different options

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛒 Astrid Mart Launcher${NC}"
echo "======================="

# Function to check dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        return 1
    fi
    
    if ! python3 -c "import pygame" 2>/dev/null; then
        echo -e "${RED}❌ pygame not installed${NC}"
        echo "Run: pip3 install pygame"
        return 1
    fi
    
    if ! python3 -c "import serial" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  pyserial not installed (barcode scanner won't work)${NC}"
        echo "Run: pip3 install pyserial"
    fi
    
    echo -e "${GREEN}✅ Dependencies OK${NC}"
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  start, run       - Start game in fullscreen"
    echo "  test, windowed   - Start game in windowed mode"
    echo "  debug            - Start game in windowed mode with debug"
    echo "  check            - Check dependencies only"
    echo "  help             - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start         # Normal fullscreen game"
    echo "  $0 test          # Test in windowed mode"
    echo "  $0 debug         # Debug mode for troubleshooting"
}

# Parse command line argument
case "${1:-start}" in
    "start"|"run"|"")
        check_dependencies || exit 1
        echo -e "${GREEN}🚀 Starting Astrid Mart (fullscreen)...${NC}"
        python3 main.py
        ;;
    "test"|"windowed")
        check_dependencies || exit 1
        echo -e "${GREEN}🧪 Starting Astrid Mart (windowed test mode)...${NC}"
        python3 main.py --windowed
        ;;
    "debug")
        check_dependencies || exit 1
        echo -e "${GREEN}🔧 Starting Astrid Mart (debug mode)...${NC}"
        python3 main.py --windowed --debug
        ;;
    "check")
        check_dependencies
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac 