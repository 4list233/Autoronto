#!/bin/bash
# Quick Linux Setup Script for aUToronto PM Dashboard
# Run this after transferring files to PC4 (Linux)

set -e  # Exit on error

echo "=========================================="
echo "aUToronto PM Dashboard - Linux Setup"
echo "=========================================="
echo ""

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"
echo ""

# Check Python version
echo "Step 1: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Create virtual environment
echo ""
echo "Step 2: Setting up virtual environment..."
cd "$PROJECT_DIR"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate and install dependencies
echo ""
echo "Step 3: Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r dashboard/requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Step 4: Creating directories..."
mkdir -p dashboard/logs
mkdir -p dashboard/.streamlit
mkdir -p data
echo "✓ Directories created"

# Check if data files exist
echo ""
echo "Step 5: Checking data files..."
if [ -f "data/children_hierarchical_4336931.json" ]; then
    echo "✓ Data files found"
else
    echo "⚠ Warning: Data files not found in data/ directory"
    echo "  You'll need to either:"
    echo "  1. Transfer data/*.json files from Mac"
    echo "  2. Set up .env file with TeamGantt API credentials"
fi

# Check .env file for API access
echo ""
echo "Step 6: Checking .env file..."
if [ -f ".env" ]; then
    echo "✓ .env file found"
else
    echo "⚠ No .env file found"
    echo "  If using live API data, create .env with:"
    echo "  TEAMGANTT_API_TOKEN=your_token_here"
fi

# Update config for Linux paths
echo ""
echo "Step 7: Updating configurations..."
# Config.json should be fine as-is

# Create systemd service file
echo ""
echo "Step 8: Creating systemd service..."
cat > /tmp/autoronto-dashboard.service <<EOF
[Unit]
Description=aUToronto PM Dashboard (Streamlit)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/dashboard
Environment="PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/.venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created at /tmp/autoronto-dashboard.service"

# Test run
echo ""
echo "Step 9: Testing dashboard..."
echo "Starting test run for 5 seconds..."
cd dashboard
timeout 5 streamlit run app.py --server.address=0.0.0.0 --server.port=8501 &> /tmp/streamlit-test.log &
TEST_PID=$!
sleep 3

if ps -p $TEST_PID > /dev/null 2>&1; then
    echo "✓ Dashboard test successful!"
    kill $TEST_PID 2>/dev/null
    wait $TEST_PID 2>/dev/null
else
    echo "✗ Dashboard failed to start"
    echo "Check logs at: /tmp/streamlit-test.log"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Install as system service (requires sudo):"
echo "   sudo cp /tmp/autoronto-dashboard.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable autoronto-dashboard"
echo "   sudo systemctl start autoronto-dashboard"
echo ""
echo "2. OR run manually for testing:"
echo "   cd $PROJECT_DIR/dashboard"
echo "   source ../.venv/bin/activate"
echo "   streamlit run app.py --server.address=0.0.0.0 --server.port=8501"
echo ""
echo "3. Access dashboard at:"
echo "   http://pm.in.autoronto.ca:8501"
echo ""
echo "4. Configure firewall (if needed):"
echo "   sudo ufw allow 8501/tcp"
echo "   sudo ufw reload"
echo ""
