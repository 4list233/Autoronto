#!/bin/bash
# Setup script for aUToronto PM Dashboard Web Service
# This script configures the dashboard to be accessible at pm.in.autoronto.ca

echo "=========================================="
echo "aUToronto PM Dashboard - Web Service Setup"
echo "=========================================="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - using launchd instead of systemd"
    SERVICE_TYPE="launchd"
else
    echo "Detected Linux - using systemd"
    SERVICE_TYPE="systemd"
fi

echo ""
echo "Step 1: Stopping any running Streamlit instances..."
pkill -f "streamlit run app.py" || echo "No running instances found"
sleep 2

echo ""
echo "Step 2: Testing Streamlit configuration..."
cd "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard"
source "../.venv/bin/activate"

# Test if Streamlit can start
echo "Starting Streamlit in test mode (will run for 5 seconds)..."
timeout 5 streamlit run app.py --server.address=0.0.0.0 --server.port=8501 &
TEST_PID=$!
sleep 3

if ps -p $TEST_PID > /dev/null; then
    echo "✓ Streamlit test successful"
    kill $TEST_PID 2>/dev/null
else
    echo "✗ Streamlit failed to start - check for errors above"
    exit 1
fi

echo ""
echo "=========================================="
echo "Manual Setup Steps:"
echo "=========================================="
echo ""
echo "1. PiHole DNS Configuration:"
echo "   - Access PiHole admin panel"
echo "   - Go to: Local DNS → DNS Records"
echo "   - Add entry:"
echo "     Domain: pm.in.autoronto.ca"
echo "     IP: <PC4's static IP>"
echo ""
echo "2. Firewall Configuration:"
echo "   Allow incoming connections on port 8501"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   macOS: System Settings → Network → Firewall"
else
    echo "   sudo ufw allow 8501/tcp"
    echo "   sudo ufw reload"
fi
echo ""
echo "3. Start the Dashboard:"
echo "   Option A - Run in terminal:"
echo "   cd /Users/5425855/Desktop/Uoft\\ Studying/Autoronto/dashboard"
echo "   source ../.venv/bin/activate"
echo "   streamlit run app.py --server.address=0.0.0.0 --server.port=8501"
echo ""
echo "   Option B - Run as background service (recommended):"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   (See setup-launchd.sh for macOS service setup)"
else
    echo "   sudo cp autoronto-dashboard.service /etc/systemd/system/"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable autoronto-dashboard"
    echo "   sudo systemctl start autoronto-dashboard"
    echo "   sudo systemctl status autoronto-dashboard"
fi
echo ""
echo "4. Test Access:"
echo "   From VPN-connected device, open browser:"
echo "   http://pm.in.autoronto.ca:8501"
echo ""
echo "=========================================="
echo "Setup script complete!"
echo "=========================================="
