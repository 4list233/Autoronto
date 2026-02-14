# aUToronto PM Dashboard - Deployment Guide

**Project**: aUToronto Project Management Dashboard  
**Deployment Date**: February 2026  
**Environment**: PC4 (Linux Ubuntu 20.04)  
**Access URL**: `http://pm.in.autoronto.ca:8501`  
**Developer**: Team Lead & Dashboard Developer  

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Infrastructure Architecture](#infrastructure-architecture)
3. [Deployment Workflow Summary](#deployment-workflow-summary)
4. [Step-by-Step Setup Instructions](#step-by-step-setup-instructions)
5. [Service Management](#service-management)
6. [Access & Testing](#access--testing)
7. [Troubleshooting](#troubleshooting)
8. [Future Enhancements](#future-enhancements)
9. [Development Notes](#development-notes)

---

## 📖 Project Overview

### What is This Dashboard?

A **Streamlit-based web dashboard** for tracking project management metrics for the aUToronto SAE competition team. It provides:

- **Weekly team utilization tracking** (hrs/wk per member, aligned with SAE WBS requirements)
- **Member performance analytics** (task-focused and hours-focused views)
- **Outlier detection** (overloaded, inactive, or underperforming members)
- **Task management** (upcoming tasks, overdue warnings, critical tasks)
- **Team-level insights** (utilization by team, cross-team comparisons)
- **All-members overview** (single page to see all members without filtering)

### Why PC4?

PC4 is an internal Linux machine (`pc4.in.autoronto.ca`) on the aUToronto VPN network, chosen because:
- Always-on availability for team members
- Accessible via internal DNS through PiHole
- No need for cloud hosting costs
- Data stays internal to the organization

---

## 🏗️ Infrastructure Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    aUToronto VPN Network                     │
│                                                               │
│  ┌──────────────┐      ┌─────────────────────────────────┐  │
│  │   PiHole DNS │─────▶│  pm.in.autoronto.ca             │  │
│  │              │      │  (resolves to 10.10.2.4)        │  │
│  └──────────────┘      └─────────────────────────────────┘  │
│                                    │                          │
│                                    ▼                          │
│                        ┌──────────────────────┐              │
│                        │   PC4 (Linux)        │              │
│                        │   10.10.2.4:8501     │              │
│                        │                      │              │
│                        │  ┌────────────────┐  │              │
│                        │  │   Systemd      │  │              │
│                        │  │   Service      │  │              │
│                        │  └───────┬────────┘  │              │
│                        │          │           │              │
│                        │          ▼           │              │
│                        │  ┌────────────────┐  │              │
│                        │  │   Streamlit    │  │              │
│                        │  │   Dashboard    │  │              │
│                        │  │   (Port 8501)  │  │              │
│                        │  └────────┬───────┘  │              │
│                        │           │          │              │
│                        │           ▼          │              │
│                        │  ┌────────────────┐  │              │
│                        │  │  TeamGantt API │  │              │
│                        │  │  + Local Cache │  │              │
│                        │  └────────────────┘  │              │
│                        └──────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure on PC4

```
/home/autoronto/Desktop/PM_Server/Autoronto/
├── dashboard/                    # Main dashboard code
│   ├── app.py                   # Streamlit entry point
│   ├── config.json              # Dashboard configuration
│   ├── pages/                   # Dashboard pages (p1-p11)
│   ├── components/              # Reusable UI components
│   ├── utils/                   # Data processing utilities
│   ├── .streamlit/              # Streamlit config
│   │   └── config.toml          # Network settings
│   └── requirements.txt         # Python dependencies
├── data/                        # TeamGantt cache (auto-generated)
├── .venv/                       # Python virtual environment
├── .env                         # API credentials (NOT in git)
└── autoronto-dashboard-pc4.service  # Systemd service file
```

### Technology Stack

- **Backend**: Python 3.8
- **Framework**: Streamlit 1.31.0
- **Data Processing**: Pandas, Plotly
- **Data Source**: TeamGantt API (REST)
- **Service Manager**: systemd
- **OS**: Ubuntu 20.04 LTS

---

## 📝 Deployment Workflow Summary

### Phase 1: Development (macOS)

1. Built dashboard locally on macOS
2. Tested with local virtual environment
3. Configured TeamGantt API integration
4. Created all dashboard pages and utilities
5. Generated configuration files

### Phase 2: Transfer to PC4 (Linux)

1. **Prepared files for transfer**:
   - Excluded: `.venv/`, `data/`, `.DS_Store`, `.env` (local only)
   - Included: All dashboard code, configs, scripts

2. **Used `rsync` to transfer**:
   ```bash
   rsync -avz \
     --exclude='.venv' \
     --exclude='data' \
     --exclude='.DS_Store' \
     --exclude='.env' \
     ~/Desktop/Uoft\ Studying/Autoronto/ \
     autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/
   ```

### Phase 3: Linux Environment Setup

1. **Installed system dependencies**:
   - Python 3.8 (already present)
   - `python3.8-venv` (for virtual environments)
   - `python3-pip` (Python package manager)

2. **Created virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Installed Python dependencies**:
   ```bash
   source .venv/bin/activate
   pip install streamlit pandas plotly python-dotenv requests
   ```

4. **Created `.env` file** with TeamGantt API credentials

### Phase 4: Systemd Service Setup

1. **Generated service file** (`autoronto-dashboard-pc4.service`)
2. **Installed service**:
   ```bash
   sudo cp autoronto-dashboard-pc4.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable autoronto-dashboard
   sudo systemctl start autoronto-dashboard
   ```

3. **Verified service status**:
   ```bash
   sudo systemctl status autoronto-dashboard
   ```

### Phase 5: Network Configuration

1. **PiHole DNS Entry**:
   - Added `pm.in.autoronto.ca` → `10.10.2.4`

2. **Firewall configuration**:
   - Allowed port 8501: `sudo ufw allow 8501/tcp`
   - (Firewall was inactive, ports already open on internal network)

3. **Streamlit network config** (`.streamlit/config.toml`):
   - Bound to `0.0.0.0:8501` for network access
   - Set server address to `pm.in.autoronto.ca`

---

## 🚀 Step-by-Step Setup Instructions

### Prerequisites

- **Access**: SSH access to PC4 (`autoronto@pc4.in.autoronto.ca`)
- **Credentials**: TeamGantt API key
- **Network**: Connected to aUToronto VPN

### 1. Initial System Setup (One-time)

```bash
# SSH into PC4
ssh autoronto@pc4.in.autoronto.ca

# Update system packages
sudo apt update

# Install required system packages
sudo apt install python3.8-venv python3-pip
```

### 2. Transfer Project Files

**From your development machine** (macOS/Linux):

```bash
# Navigate to project directory
cd ~/Desktop/Uoft\ Studying/Autoronto/

# Transfer to PC4 (exclude unnecessary files)
rsync -avz \
  --exclude='.venv' \
  --exclude='data' \
  --exclude='.DS_Store' \
  --exclude='.env' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  ./ \
  autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/
```

### 3. Setup Python Environment on PC4

```bash
# SSH into PC4
ssh autoronto@pc4.in.autoronto.ca

# Navigate to project directory
cd ~/Desktop/PM_Server/Autoronto

# Run automated setup script
chmod +x dashboard/setup-linux.sh
./dashboard/setup-linux.sh
```

**What the script does:**
- Creates Python virtual environment (`.venv/`)
- Installs all dependencies from `requirements.txt`
- Creates `data/` directory for TeamGantt cache
- Generates systemd service file
- Tests the dashboard startup

### 4. Configure API Credentials

```bash
# Create .env file
nano .env
```

**Add this content** (replace with actual credentials):

```bash
TEAMGANTT_API_KEY=your_actual_api_key_here
TEAMGANTT_PROJECT_ID=your_project_id
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

**Set secure permissions:**
```bash
chmod 600 .env
```

### 5. Install as System Service

```bash
# Copy service file to systemd
sudo cp /tmp/autoronto-dashboard.service /etc/systemd/system/autoronto-dashboard.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable autoronto-dashboard

# Start service
sudo systemctl start autoronto-dashboard

# Check status
sudo systemctl status autoronto-dashboard
```

**Expected output:**
```
● autoronto-dashboard.service - aUToronto PM Dashboard
   Loaded: loaded (/etc/systemd/system/autoronto-dashboard.service; enabled)
   Active: active (running) since Sat 2026-02-14 ...
```

### 6. Configure Firewall (if needed)

```bash
# Allow port 8501
sudo ufw allow 8501/tcp

# Check firewall status
sudo ufw status
```

### 7. Verify Installation

```bash
# Test local access
curl http://localhost:8501

# Check service logs
sudo journalctl -u autoronto-dashboard -f

# View dashboard process
ps aux | grep streamlit
```

---

## 🛠️ Service Management

### Common Commands

```bash
# Start the dashboard
sudo systemctl start autoronto-dashboard

# Stop the dashboard
sudo systemctl stop autoronto-dashboard

# Restart the dashboard
sudo systemctl restart autoronto-dashboard

# Check status
sudo systemctl status autoronto-dashboard

# View live logs
sudo journalctl -u autoronto-dashboard -f

# View last 100 log lines
sudo journalctl -u autoronto-dashboard -n 100

# Enable auto-start on boot
sudo systemctl enable autoronto-dashboard

# Disable auto-start
sudo systemctl disable autoronto-dashboard
```

### Updating the Dashboard

When code changes are made:

```bash
# 1. Transfer updated files from dev machine
rsync -avz --exclude='.venv' --exclude='data' \
  ./ autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/

# 2. SSH into PC4
ssh autoronto@pc4.in.autoronto.ca

# 3. Navigate to project
cd ~/Desktop/PM_Server/Autoronto

# 4. Update dependencies (if requirements.txt changed)
source .venv/bin/activate
pip install -r dashboard/requirements.txt

# 5. Restart service
sudo systemctl restart autoronto-dashboard

# 6. Verify
sudo systemctl status autoronto-dashboard
```

### Manual Testing (without systemd)

```bash
# SSH into PC4
ssh autoronto@pc4.in.autoronto.ca

# Navigate to project
cd ~/Desktop/PM_Server/Autoronto/dashboard

# Activate virtual environment
source ../.venv/bin/activate

# Run Streamlit manually
streamlit run app.py --server.address=0.0.0.0 --server.port=8501

# Stop with Ctrl+C
```

---

## 🌐 Access & Testing

### Access URLs

**Primary (Internal DNS):**
- `http://pm.in.autoronto.ca:8501`

**Alternative (Direct IP):**
- `http://10.10.2.4:8501`

**Requirements:**
- Must be connected to aUToronto VPN
- PiHole DNS must resolve `pm.in.autoronto.ca` to `10.10.2.4`

### Testing Checklist

- [ ] Can access dashboard from VPN-connected device
- [ ] All pages load without errors
- [ ] Data refreshes successfully
- [ ] Charts and tables render correctly
- [ ] Member data displays across all views
- [ ] Service restarts automatically after reboot

### Performance Checks

```bash
# On PC4, check resource usage
htop  # or top

# Check memory usage
free -h

# Check disk space
df -h

# Monitor dashboard process
ps aux | grep streamlit

# Check network connections
sudo netstat -tulpn | grep 8501
```

---

## 🐛 Troubleshooting

### Issue: Dashboard won't start

**Check service status:**
```bash
sudo systemctl status autoronto-dashboard
```

**View detailed logs:**
```bash
sudo journalctl -u autoronto-dashboard -n 50
```

**Common causes:**
- Missing `.env` file or invalid API credentials
- Port 8501 already in use
- Virtual environment corrupted
- Missing Python dependencies

**Fix:**
```bash
# Recreate virtual environment
cd ~/Desktop/PM_Server/Autoronto
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r dashboard/requirements.txt

# Restart service
sudo systemctl restart autoronto-dashboard
```

---

### Issue: Can't access dashboard from browser

**Check if service is running:**
```bash
sudo systemctl status autoronto-dashboard
```

**Check if port is listening:**
```bash
sudo netstat -tulpn | grep 8501
```

**Test local access on PC4:**
```bash
curl http://localhost:8501
```

**Check firewall:**
```bash
sudo ufw status
```

**Verify DNS resolution** (from your device):
```bash
ping pm.in.autoronto.ca
# Should resolve to 10.10.2.4
```

**Check VPN connection:**
- Ensure you're connected to aUToronto VPN
- Verify you can ping PC4: `ping 10.10.2.4`

---

### Issue: Dashboard loads but pages are blank

**Possible causes:**
- API credentials incorrect
- TeamGantt API rate limiting
- Data cache corruption

**Fix:**
```bash
# Check logs for API errors
sudo journalctl -u autoronto-dashboard -n 100 | grep -i error

# Clear cache
cd ~/Desktop/PM_Server/Autoronto
rm -rf data/*.json data/*.csv

# Restart service
sudo systemctl restart autoronto-dashboard
```

---

### Issue: Service doesn't restart after reboot

**Check if service is enabled:**
```bash
sudo systemctl is-enabled autoronto-dashboard
```

**Enable if needed:**
```bash
sudo systemctl enable autoronto-dashboard
```

**Test reboot persistence:**
```bash
sudo reboot
# Wait for PC4 to restart, then check:
sudo systemctl status autoronto-dashboard
```

---

### Issue: "KeyError: member_hours_per_week"

**This was fixed in the code, but if it reappears:**

Check `config.json` has correct structure:
```bash
cat ~/Desktop/PM_Server/Autoronto/dashboard/config.json
```

Should NOT contain `member_hours_per_week` or `lead_hours_per_week` (removed per requirements).

---

## 🚀 Future Enhancements

### 1. Remove Port from URL (Nginx Reverse Proxy)

**Goal**: Access at `http://pm.in.autoronto.ca` instead of `:8501`

**See**: `NGINX_SETUP_GUIDE.md` for complete instructions

**Quick summary:**
```bash
# Install nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/pm-dashboard
# (paste nginx config)

# Enable and start
sudo ln -s /etc/nginx/sites-available/pm-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo ufw allow 80/tcp
```

### 2. HTTPS Support

**Option**: Self-signed certificate for internal use

See `generate-ssl-cert.sh` and `nginx-pm-dashboard-ssl.conf`

### 3. Automated Backups

```bash
# Add to crontab
0 2 * * * rsync -avz /home/autoronto/Desktop/PM_Server/Autoronto/data/ /backup/dashboard-data/
```

### 4. Monitoring & Alerts

- Set up service monitoring (e.g., Prometheus + Grafana)
- Email alerts if service goes down
- Resource usage monitoring

### 5. CI/CD Pipeline

- Automated deployment from git repository
- Automatic restart on code push
- Health checks after deployment

---

## 💡 Development Notes

### Project Background

This dashboard was created to replace TeamGantt's default UI for the aUToronto team, because:

1. **SAE Competition Requirements**: Need to present weekly WBS tracking (hours/week per person)
2. **Team Management**: Need to identify overloaded/inactive members quickly
3. **Proactive Planning**: Need visibility into upcoming tasks (1-4 weeks ahead)
4. **Cross-Team Visibility**: Need to see all members without filtering by team

### Key Design Decisions

**Removed "Expected Hours" Metric:**
- Original plan included expected hours per member
- Removed because it was an unused/unmaintained component
- Now focuses purely on actual hours logged

**Week-Based Tracking:**
- All metrics calculated Monday-Friday per week
- Aligns with SAE competition WBS presentation requirements
- Historical view: 8 weeks back
- Lookahead: 4 weeks forward

**All-Members View:**
- Single page to see all members across all teams
- Eliminates need to filter by team to find outliers
- Sortable by tasks or hours (ascending/descending)

**Task vs Hours Focus:**
- Two distinct views for member analysis
- Task-focused: See who's taking on too many/few tasks
- Hours-focused: See who's logging excessive/no hours

### Configuration Files

**`dashboard/config.json`**:
- Team definitions and lead assignments
- Outlier thresholds (high hours, high tasks, inactive)
- Week tracking settings (historical, lookahead)
- Critical task thresholds

**`dashboard/.streamlit/config.toml`**:
- Network binding (0.0.0.0 for external access)
- Server address for proper URL generation
- Theme customization

**`.env`** (NOT in git):
- TeamGantt API credentials
- Should never be committed to version control

### API Integration

**TeamGantt API:**
- REST API for project data
- Authentication: Bearer token
- Rate limiting: Be mindful of request frequency
- Local caching in `data/` directory to reduce API calls

### Testing Workflow

1. **Local development** (macOS): Direct `streamlit run`
2. **Transfer to PC4**: `rsync` with exclusions
3. **Linux testing**: Manual `streamlit run` to verify
4. **Service deployment**: systemd for production

---

## 📞 Support & Contacts

**Dashboard Developer**: [Your Team Lead]  
**PC4 Administrator**: autoronto team  
**Network/DNS**: aUToronto IT team  

**Documentation Files:**
- `DEPLOYMENT_GUIDE.md` (this file)
- `NGINX_SETUP_GUIDE.md` (reverse proxy setup)
- `LINUX_SETUP_GUIDE.md` (detailed Linux setup)
- `DASHBOARD_REQUIREMENTS.md` (feature requirements)
- `TEAMGANTT_TIME_TRACKING_GUIDE.md` (time tracking guide)

---

## 🎯 Quick Reference Commands

### On PC4:

```bash
# Check service status
sudo systemctl status autoronto-dashboard

# Restart dashboard
sudo systemctl restart autoronto-dashboard

# View logs
sudo journalctl -u autoronto-dashboard -f

# Manual run (for testing)
cd ~/Desktop/PM_Server/Autoronto/dashboard
source ../.venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

### From Dev Machine:

```bash
# Transfer updated code
rsync -avz --exclude='.venv' --exclude='data' \
  ~/Desktop/Uoft\ Studying/Autoronto/ \
  autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/

# SSH to PC4
ssh autoronto@pc4.in.autoronto.ca

# Restart after update
ssh autoronto@pc4.in.autoronto.ca "sudo systemctl restart autoronto-dashboard"
```

---

## ✅ Deployment Checklist

**Initial Setup:**
- [ ] PC4 has Python 3.8+ installed
- [ ] `python3.8-venv` and `python3-pip` installed
- [ ] Project files transferred to `/home/autoronto/Desktop/PM_Server/Autoronto/`
- [ ] Virtual environment created (`.venv/`)
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `.env` file created with API credentials
- [ ] `data/` directory created
- [ ] Systemd service file installed
- [ ] Service enabled and started
- [ ] Firewall configured (port 8501)
- [ ] PiHole DNS entry created (`pm.in.autoronto.ca`)

**Testing:**
- [ ] Service starts without errors
- [ ] Dashboard accessible locally (`curl http://localhost:8501`)
- [ ] Dashboard accessible from VPN device
- [ ] All pages load correctly
- [ ] Data displays properly
- [ ] Service survives PC4 reboot

**Documentation:**
- [ ] `.env.example` created (template without real credentials)
- [ ] README updated with access instructions
- [ ] Deployment guide shared with team
- [ ] Credentials stored securely

---

**Last Updated**: February 14, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready
