#!/bin/bash
# Pre-transfer checklist and preparation script
# Run this on Mac BEFORE transferring to Linux

echo "=========================================="
echo "Pre-Transfer Checklist"
echo "=========================================="
echo ""

PROJECT_DIR="/Users/5425855/Desktop/Uoft Studying/Autoronto"
cd "$PROJECT_DIR"

echo "Checking what will be transferred..."
echo ""

# Check dashboard files
echo "✓ Dashboard code:"
ls -lh dashboard/*.py 2>/dev/null | wc -l | xargs echo "  - Python files:"
ls -lh dashboard/pages/*.py 2>/dev/null | wc -l | xargs echo "  - Page files:"
ls -lh dashboard/utils/*.py 2>/dev/null | wc -l | xargs echo "  - Util files:"
ls -lh dashboard/components/*.py 2>/dev/null | wc -l | xargs echo "  - Component files:"

echo ""
echo "✓ Configuration:"
ls -lh dashboard/config.json dashboard/.streamlit/config.toml 2>/dev/null | awk '{print "  -", $9}'

echo ""
echo "✓ Data files:"
ls -lh data/*.json 2>/dev/null | awk '{print "  -", $9, "("$5")"}'

echo ""
echo "✓ Documentation:"
ls -lh *.md 2>/dev/null | awk '{print "  -", $9}'

echo ""
echo "⚠ Files to EXCLUDE (will not transfer):"
du -sh .venv 2>/dev/null && echo "  - .venv/ (will recreate on Linux)"
find . -type d -name __pycache__ 2>/dev/null | wc -l | xargs echo "  - __pycache__ directories:"
find . -name ".DS_Store" 2>/dev/null | wc -l | xargs echo "  - .DS_Store files:"

echo ""
echo "=========================================="
echo "Recommended Transfer Command:"
echo "=========================================="
echo ""
echo "rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '.DS_Store' \\"
echo "  --exclude '*.pyc' --exclude 'logs/*' \\"
echo "  \"$PROJECT_DIR/\" \\"
echo "  user@pc4.in.autoronto.ca:/home/user/Autoronto/"
echo ""
echo "Or using Git (if data files are in .gitignore):"
echo "1. On Linux: git clone https://github.com/4list233/Autoronto.git"
echo "2. Then rsync only data files:"
echo "   rsync -avz \"$PROJECT_DIR/data/\" user@pc4.in.autoronto.ca:/home/user/Autoronto/data/"
echo ""
echo "=========================================="
echo "After Transfer:"
echo "=========================================="
echo "1. SSH into PC4: ssh user@pc4.in.autoronto.ca"
echo "2. Run setup: cd Autoronto && ./dashboard/setup-linux.sh"
echo "3. Follow prompts to install as service"
echo ""
