# Dashboard Deployment Workflow - Visual Summary

This document provides a visual overview of the complete deployment workflow from development to production.

---

## 🎯 Overview: Dev to Production Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                    DEVELOPMENT WORKFLOW                               │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

   ┌──────────────────┐
   │  macOS Dev       │
   │  Environment     │
   │                  │
   │  - Build code    │
   │  - Local testing │
   │  - Git commits   │
   └────────┬─────────┘
            │
            │ rsync transfer
            │ (excludes: .venv, data, .env)
            │
            ▼
   ┌──────────────────┐
   │  PC4 (Linux)     │
   │  Production      │
   │                  │
   │  - Setup venv    │
   │  - Install deps  │
   │  - Create .env   │
   │  - Run service   │
   └────────┬─────────┘
            │
            │ systemd manages
            │
            ▼
   ┌──────────────────┐
   │  Streamlit       │
   │  Dashboard       │
   │  (Port 8501)     │
   └────────┬─────────┘
            │
            │ VPN + DNS
            │
            ▼
   ┌──────────────────┐
   │  Team Members    │
   │  (Browsers)      │
   │                  │
   │  pm.in.          │
   │  autoronto.ca    │
   │  :8501           │
   └──────────────────┘
```

---

## 📋 Step-by-Step Workflow

### Phase 1: Development (macOS)

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Local Development                                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Location: ~/Desktop/Uoft Studying/Autoronto/                │
│                                                               │
│  Actions:                                                     │
│    1. Create/edit dashboard code                             │
│    2. Install dependencies in local .venv                    │
│    3. Test with: streamlit run dashboard/app.py              │
│    4. Commit changes to git                                  │
│                                                               │
│  Key Files:                                                   │
│    ✓ dashboard/app.py                                        │
│    ✓ dashboard/pages/*.py                                    │
│    ✓ dashboard/config.json                                   │
│    ✓ dashboard/requirements.txt                              │
│    ✓ .env (API credentials - NOT in git)                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Transfer to Production

```
┌─────────────────────────────────────────────────────────────┐
│  Step 2: File Transfer (macOS → PC4)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Command:                                                     │
│    rsync -avz \                                              │
│      --exclude='.venv' \                                     │
│      --exclude='data' \                                      │
│      --exclude='.DS_Store' \                                 │
│      --exclude='.env' \                                      │
│      ./ \                                                    │
│      autoronto@pc4.in.autoronto.ca:\                         │
│        /home/autoronto/Desktop/PM_Server/Autoronto/          │
│                                                               │
│  What Gets Transferred:                                       │
│    ✅ All dashboard code                                     │
│    ✅ Config files                                           │
│    ✅ Setup scripts                                          │
│    ✅ Documentation                                          │
│                                                               │
│  What Stays Local:                                            │
│    ❌ .venv/ (rebuilt on PC4)                                │
│    ❌ data/ (cache, regenerated)                             │
│    ❌ .env (manually created on PC4)                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Linux Environment Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Step 3: PC4 Environment Setup                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Location: /home/autoronto/Desktop/PM_Server/Autoronto/      │
│                                                               │
│  Actions:                                                     │
│    1. Install system packages                                │
│       sudo apt install python3.8-venv python3-pip            │
│                                                               │
│    2. Run automated setup                                    │
│       ./dashboard/setup-linux.sh                             │
│                                                               │
│  What setup-linux.sh Does:                                   │
│    ├─ Creates .venv/ directory                               │
│    ├─ Installs Python dependencies                           │
│    ├─ Creates data/ directory                                │
│    ├─ Generates systemd service file                         │
│    └─ Tests dashboard startup                                │
│                                                               │
│    3. Create .env file                                       │
│       nano .env                                              │
│       (add TeamGantt API credentials)                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Phase 4: Service Installation

```
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Systemd Service Setup                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Service File: autoronto-dashboard-pc4.service               │
│  Location: /etc/systemd/system/                              │
│                                                               │
│  Commands:                                                    │
│    1. Copy service file                                      │
│       sudo cp /tmp/autoronto-dashboard.service \             │
│         /etc/systemd/system/                                 │
│                                                               │
│    2. Reload systemd                                         │
│       sudo systemctl daemon-reload                           │
│                                                               │
│    3. Enable auto-start                                      │
│       sudo systemctl enable autoronto-dashboard              │
│                                                               │
│    4. Start service                                          │
│       sudo systemctl start autoronto-dashboard               │
│                                                               │
│    5. Verify status                                          │
│       sudo systemctl status autoronto-dashboard              │
│                                                               │
│  Service Configuration:                                       │
│    - User: autoronto                                         │
│    - WorkingDirectory: .../PM_Server/Autoronto/dashboard     │
│    - ExecStart: ../.venv/bin/streamlit run app.py           │
│    - Restart: always (auto-restart on failure)              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Phase 5: Network & Access

```
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Network Configuration                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  A. PiHole DNS Entry                                         │
│     pm.in.autoronto.ca → 10.10.2.4                           │
│                                                               │
│  B. PC4 Firewall                                             │
│     sudo ufw allow 8501/tcp                                  │
│     (firewall was inactive, ports already open)              │
│                                                               │
│  C. Streamlit Network Config                                 │
│     File: dashboard/.streamlit/config.toml                   │
│     - server.address = "0.0.0.0" (bind all interfaces)       │
│     - server.port = 8501                                     │
│     - browser.serverAddress = "pm.in.autoronto.ca"           │
│                                                               │
│  D. Access URLs                                              │
│     ✅ http://pm.in.autoronto.ca:8501 (internal DNS)         │
│     ✅ http://10.10.2.4:8501 (direct IP)                     │
│                                                               │
│  Requirements:                                                │
│     - Connected to aUToronto VPN                             │
│     - PiHole DNS configured                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Update Workflow (After Initial Deployment)

```
┌──────────────┐
│ Code Change  │
│ on Dev Mac   │
└──────┬───────┘
       │
       │ 1. Test locally
       │    streamlit run dashboard/app.py
       │
       ▼
┌──────────────┐
│ Git Commit   │
│ (optional)   │
└──────┬───────┘
       │
       │ 2. Transfer to PC4
       │    rsync -avz ...
       │
       ▼
┌──────────────┐
│ Update Deps? │
│ (if needed)  │
└──────┬───────┘
       │
       │ 3. SSH into PC4
       │    source .venv/bin/activate
       │    pip install -r requirements.txt
       │
       ▼
┌──────────────┐
│ Restart      │
│ Service      │
└──────┬───────┘
       │
       │ 4. Restart
       │    sudo systemctl restart autoronto-dashboard
       │
       ▼
┌──────────────┐
│ Verify       │
│ in Browser   │
└──────────────┘
       │
       │ 5. Test
       │    http://pm.in.autoronto.ca:8501
       │
       ▼
┌──────────────┐
│ ✅ Live!     │
└──────────────┘
```

---

## 🏗️ System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                        aUToronto VPN Network                           │
│                           (Internal Only)                              │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Team Member  │         │  Team Member  │         │  Team Member  │
│  Laptop/PC    │         │  Laptop/PC    │         │  Laptop/PC    │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                          │                          │
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                                   │ http://pm.in.autoronto.ca:8501
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │   PiHole DNS        │
                        │   (Name Resolution) │
                        └──────────┬──────────┘
                                   │
                                   │ Resolves to 10.10.2.4
                                   │
                                   ▼
        ┌──────────────────────────────────────────────────┐
        │              PC4 (Linux Ubuntu 20.04)            │
        │              IP: 10.10.2.4                       │
        │                                                  │
        │   ┌────────────────────────────────────────┐    │
        │   │         Systemd Service                │    │
        │   │   autoronto-dashboard.service          │    │
        │   │                                        │    │
        │   │   - Auto-starts on boot                │    │
        │   │   - Auto-restarts on failure           │    │
        │   │   - Runs as 'autoronto' user           │    │
        │   └─────────────┬──────────────────────────┘    │
        │                 │                                │
        │                 ▼                                │
        │   ┌────────────────────────────────────────┐    │
        │   │      Python Virtual Environment        │    │
        │   │         (.venv/)                       │    │
        │   │                                        │    │
        │   │   ┌──────────────────────────────┐    │    │
        │   │   │   Streamlit Server           │    │    │
        │   │   │   Port: 8501                 │    │    │
        │   │   │   Bound to: 0.0.0.0          │    │    │
        │   │   │                              │    │    │
        │   │   │   Dependencies:              │    │    │
        │   │   │   - streamlit                │    │    │
        │   │   │   - pandas                   │    │    │
        │   │   │   - plotly                   │    │    │
        │   │   │   - python-dotenv            │    │    │
        │   │   │   - requests                 │    │    │
        │   │   └──────────┬───────────────────┘    │    │
        │   │              │                         │    │
        │   │              ▼                         │    │
        │   │   ┌──────────────────────────────┐    │    │
        │   │   │   Dashboard Application      │    │    │
        │   │   │   (app.py + pages/)          │    │    │
        │   │   └──────────┬───────────────────┘    │    │
        │   └──────────────┼──────────────────────────┘    │
        │                  │                                │
        │                  ▼                                │
        │   ┌────────────────────────────────────────┐    │
        │   │      Data Layer                        │    │
        │   │                                        │    │
        │   │   ┌──────────────────────────────┐    │    │
        │   │   │   Local Cache (data/)        │    │    │
        │   │   │   - tasks.json               │    │    │
        │   │   │   - members.csv              │    │    │
        │   │   └──────────────────────────────┘    │    │
        │   │              │                         │    │
        │   │              │ API Calls               │    │
        │   │              ▼                         │    │
        │   │   ┌──────────────────────────────┐    │    │
        │   │   │   TeamGantt API              │    │    │
        │   │   │   (External)                 │    │    │
        │   │   │   - Project data             │    │    │
        │   │   │   - Time tracking            │    │    │
        │   │   │   - Task assignments         │    │    │
        │   │   └──────────────────────────────┘    │    │
        │   └────────────────────────────────────────┘    │
        │                                                  │
        └──────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

```
1. User Opens Browser
   └─> http://pm.in.autoronto.ca:8501

2. DNS Resolution (PiHole)
   └─> pm.in.autoronto.ca → 10.10.2.4

3. HTTP Request to PC4
   └─> PC4:8501 (Streamlit listening)

4. Streamlit Processes Request
   ├─> Check local cache (data/)
   │   ├─> Cache hit? Return data
   │   └─> Cache miss? → API call
   │
   └─> TeamGantt API Request
       ├─> GET /api/v1/projects/{id}/tasks
       ├─> GET /api/v1/projects/{id}/resources
       └─> GET /api/v1/projects/{id}/time_entries
       
5. Data Processing
   ├─> Parse API response
   ├─> Calculate weekly metrics
   ├─> Identify outliers
   ├─> Generate charts
   └─> Cache results (data/)

6. Render HTML Response
   └─> Streamlit sends HTML + JavaScript

7. Browser Displays Dashboard
   └─> User interacts with UI

8. User Changes Page/Filters
   └─> WebSocket updates (real-time)
```

---

## 🔐 Security & Access Control

```
┌─────────────────────────────────────────────────────────────┐
│  Security Layers                                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Layer 1: VPN Requirement                                    │
│    ✓ Must be connected to aUToronto VPN                     │
│    ✓ Prevents external access                               │
│                                                               │
│  Layer 2: Internal Network                                   │
│    ✓ PC4 IP: 10.10.2.4 (private network)                    │
│    ✓ Not exposed to internet                                │
│                                                               │
│  Layer 3: DNS Resolution                                     │
│    ✓ PiHole internal DNS only                               │
│    ✓ pm.in.autoronto.ca resolves internally                 │
│                                                               │
│  Layer 4: API Credentials                                    │
│    ✓ TeamGantt API key in .env file                         │
│    ✓ File permissions: 600 (owner read/write only)          │
│    ✓ NOT committed to git                                   │
│                                                               │
│  Layer 5: Systemd Service                                    │
│    ✓ Runs as 'autoronto' user (not root)                    │
│    ✓ Limited permissions                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Service Management Commands

```
┌──────────────────────────────────────────────────────────────┐
│  Systemd Service Control                                      │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Check Status:                                                │
│    sudo systemctl status autoronto-dashboard                  │
│                                                                │
│  Start/Stop/Restart:                                          │
│    sudo systemctl start autoronto-dashboard                   │
│    sudo systemctl stop autoronto-dashboard                    │
│    sudo systemctl restart autoronto-dashboard                 │
│                                                                │
│  Enable/Disable Auto-start:                                   │
│    sudo systemctl enable autoronto-dashboard                  │
│    sudo systemctl disable autoronto-dashboard                 │
│                                                                │
│  View Logs:                                                   │
│    sudo journalctl -u autoronto-dashboard -f   (live tail)    │
│    sudo journalctl -u autoronto-dashboard -n 100  (last 100)  │
│                                                                │
│  Reload Service File:                                         │
│    sudo systemctl daemon-reload                               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 📈 Monitoring

```
┌──────────────────────────────────────────────────────────────┐
│  Health Checks                                                │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Service Status                                            │
│     sudo systemctl status autoronto-dashboard                 │
│     Expected: "active (running)"                              │
│                                                                │
│  2. Process Check                                             │
│     ps aux | grep streamlit                                   │
│     Expected: streamlit process with PID                      │
│                                                                │
│  3. Port Listening                                            │
│     sudo netstat -tulpn | grep 8501                           │
│     Expected: LISTEN on 0.0.0.0:8501                          │
│                                                                │
│  4. HTTP Response                                             │
│     curl http://localhost:8501                                │
│     Expected: HTML content returned                           │
│                                                                │
│  5. Resource Usage                                            │
│     htop  (or top)                                            │
│     Expected: Reasonable CPU/memory usage                     │
│                                                                │
│  6. Disk Space                                                │
│     df -h                                                     │
│     Expected: Sufficient space in /home partition             │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **Deployment Location**: PC4 at `/home/autoronto/Desktop/PM_Server/Autoronto/`
2. **Service Management**: systemd handles auto-start and restarts
3. **Access**: VPN-only, internal DNS via PiHole
4. **Updates**: rsync from dev → restart service on PC4
5. **Monitoring**: systemctl status + journalctl for logs
6. **Security**: .env file with API credentials (not in git)

---

**For detailed instructions, see:**
- `DEPLOYMENT_GUIDE.md` - Complete deployment documentation
- `QUICK_START.md` - Quick reference for developers
- `NGINX_SETUP_GUIDE.md` - How to remove `:8501` from URL

**Access**: `http://pm.in.autoronto.ca:8501`  
**Status**: ✅ Production Ready
