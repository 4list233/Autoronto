#!/bin/bash
# Quick start script for PM Dashboard
# Runs Streamlit accessible on network at pm.in.autoronto.ca:8501

echo "Starting aUToronto PM Dashboard..."
echo "Access at: http://pm.in.autoronto.ca:8501"
echo "Press Ctrl+C to stop"
echo ""

cd "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard"
source "../.venv/bin/activate"
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
