#!/bin/bash
# OpenBro Installation Script
# Download and run with: curl -fsSL https://raw.githubusercontent.com/lazarusrolando/OpenBro/main/install.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OpenBro Installation Script${NC}"
echo "============================"

# Check Python version
python_version=$(python3 --version 2>/dev/null || python --version 2>/dev/null || echo "Python not found")
if [[ $python_version == "Python not found" ]]; then
    echo -e "${RED}Error: Python 3.8+ is required but not found.${NC}"
    echo "Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Extract version numbers
if [[ $python_version == Python* ]]; then
    ver_str=${python_version#Python }
else
    ver_str=$python_version
fi

# Check if version is at least 3.8
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${RED}Error: Python 3.8+ is required. You have: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python version OK: $python_version${NC}"

# Create temporary directory for installation
TEMP_DIR=$(mktemp -d)
echo -e "${GREEN}✓ Created temporary directory: $TEMP_DIR${NC}"

# Clone the repository
echo -e "${YELLOW}Cloning OpenBro repository...${NC}"
if git clone https://github.com/lazarusrolando/OpenBro.git "$TEMP_DIR/OpenBro"; then
    echo -e "${GREEN}✓ Repository cloned successfully${NC}"
else
    echo -e "${RED}Error: Failed to clone repository${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Change to project directory
cd "$TEMP_DIR/OpenBro"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if pip install -r requirements-cpu.txt; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}Error: Failed to install dependencies${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Install the package
echo -e "${YELLOW}Installing OpenBro package...${NC}"
if pip install -e .; then
    echo -e "${GREEN}✓ OpenBro installed successfully${NC}"
else
    echo -e "${RED}Error: Failed to install OpenBro package${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Clean up
cd /
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓ Cleaned up temporary files${NC}"

# Success message
echo -e "${GREEN}"
echo "============================"
echo "OpenBro installed successfully!"
echo "============================"
echo -e "${NC}"
echo "You can now run OpenBro from any terminal:"
echo "  openbro"
echo ""
echo "Or to see help:"
echo "  openbro --help"
echo ""
echo "To start chatting:"
echo "  openbro chat"
echo ""
echo "To start training:"
echo "  openbro train"
echo ""
echo -e "${YELLOW}Enjoy your cyberpunk AI experience!${NC}"