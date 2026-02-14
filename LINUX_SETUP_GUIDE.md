# Linux Transfer & Setup Guide
## Moving PM Dashboard from Mac to PC4 (Linux)

This guide covers everything needed to transfer and run the dashboard on a Linux system.

---

## 📦 Step 1: Files to Transfer

### **Required Files** (Must transfer):
```
Autoronto/
├── dashboard/                    # Entire dashboard folder
│   ├── app.py
│   ├── config.json
│   ├── requirements.txt
│   ├── pages/                   # All Python files
│   ├── utils/                   # All Python files
│   ├── components/              # All Python files
│   └── .streamlit/config.toml
├── data/                         # Data files (if using cached mode)
│   ├── children_hierarchical_4336931.json
│   ├── children_flat_4336931.json
│   └── project_4336931.json
└── .gitignore                    # Good practice to include
```

### **Optional Files**:
```
├── .env                          # If using live TeamGantt API
├── DASHBOARD_REQUIREMENTS.md     # Documentation
├── DASHBOARD_IMPLEMENTATION_COMPLETE.md
└── WEBSERVER_SETUP_GUIDE.md
```

### **Files to EXCLUDE** (Don't transfer):
```
├── .venv/                        # Will recreate on Linux
├── __pycache__/                  # Python cache
├── .DS_Store                     # Mac-specific
├── dashboard/logs/               # Old logs
└── ca.autoronto.pm-dashboard.plist  # Mac-only service file
```

---

## 🚀 Step 2: Transfer Methods

### **Option A: Using rsync (Recommended)**
```bash
# From Mac, run:
rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '.DS_Store' \
  "/Users/5425855/Desktop/Uoft Studying/Autoronto/" \
  user@pc4.in.autoronto.ca:/home/user/Autoronto/
```

### **Option B: Using scp**
```bash
# From Mac, run:
scp -r "/Users/5425855/Desktop/Uoft Studying/Autoronto" \
  user@pc4.in.autoronto.ca:/home/user/
```

### **Option C: Using Git**
```bash
# Already pushed to GitHub, so on PC4:
cd /home/user
git clone https://github.com/4list233/Autoronto.git
cd Autoronto

# Transfer data files separately (not in git)
# Use rsync or scp for data/ folder
```

---

## 🔧 Step 3: Setup on Linux

### **Quick Setup (Automated)**:
```bash
# SSH into PC4
ssh user@pc4.in.autoronto.ca

# Navigate to project
cd /home/user/Autoronto

# Run setup script
./dashboard/setup-linux.sh
```

### **Manual Setup**:

#### 1. Install Python (if not installed)
```bash
# Check Python version
python3 --version  # Need 3.8 or higher

# If not installed (Ubuntu/Debian):
sudo apt update
sudo apt install python3 python3-pip python3-venv

# If not installed (RHEL/CentOS):
sudo yum install python3 python3-pip
```

#### 2. Create Virtual Environment
```bash
cd /home/user/Autoronto
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r dashboard/requirements.txt
```

#### 4. Create Directories
```bash
mkdir -p dashboard/logs
mkdir -p data
```

#### 5. Update Config (if needed)
```bash
# Edit dashboard/config.json
# Make sure data_source is set correctly:
# - "cached" if you have data/*.json files
# - "live" if using TeamGantt API (need .env file)
nano dashboard/config.json
```

---

## 🔐 Step 4: Configure Environment

### **If Using Live API** (Optional):

Create `.env` file:
```bash
nano .env
```

Add:
```
TEAMGANTT_API_TOKEN=your_token_here
```

Make it secure:
```bash
chmod 600 .env
```

---

## 🌐 Step 5: Test the Dashboard

### **Quick Test**:
```bash
cd /home/user/Autoronto/dashboard
source ../.venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

**Access at**: `http://localhost:8501` or `http://pm.in.autoronto.ca:8501`

Press `Ctrl+C` to stop.

---

## ⚙️ Step 6: Set Up as System Service

### **Create Systemd Service**:

```bash
# The setup script creates this file, or create manually:
sudo nano /etc/systemd/system/autoronto-dashboard.service
```

**Content** (adjust USER and paths):
```ini
[Unit]
Description=aUToronto PM Dashboard (Streamlit)
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Autoronto/dashboard
Environment="PATH=/home/YOUR_USERNAME/Autoronto/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/YOUR_USERNAME/Autoronto/.venv/bin/streamlit run app.py --server.address=0.0.0.0 --server.port=8501
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/Autoronto/dashboard/logs/dashboard.log
StandardError=append:/home/YOUR_USERNAME/Autoronto/dashboard/logs/dashboard.error.log

[Install]
WantedBy=multi-user.target
```

### **Enable and Start Service**:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable autoronto-dashboard

# Start service now
sudo systemctl start autoronto-dashboard

# Check status
sudo systemctl status autoronto-dashboard
```

### **Manage Service**:
```bash
# Stop service
sudo systemctl stop autoronto-dashboard

# Restart service
sudo systemctl restart autoronto-dashboard

# View logs
sudo journalctl -u autoronto-dashboard -f

# Or view file logs
tail -f ~/Autoronto/dashboard/logs/dashboard.log
```

---

## 🔥 Step 7: Configure Firewall

### **Allow Port 8501**:

**Ubuntu/Debian (ufw)**:
```bash
sudo ufw allow 8501/tcp
sudo ufw reload
sudo ufw status
```

**RHEL/CentOS (firewalld)**:
```bash
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

**Check if port is open**:
```bash
sudo netstat -tulpn | grep 8501
# Or
sudo ss -tulpn | grep 8501
```

---

## ✅ Step 8: Verify Everything Works

### **1. Check Service Status**:
```bash
sudo systemctl status autoronto-dashboard
# Should show "active (running)"
```

### **2. Test Local Access**:
```bash
curl http://localhost:8501
# Should return HTML
```

### **3. Test Network Access** (from another machine):
```bash
curl http://pm.in.autoronto.ca:8501
# Should return HTML
```

### **4. Open in Browser**:
```
http://pm.in.autoronto.ca:8501
```

---

## 🐛 Troubleshooting

### **Dashboard Won't Start**:
```bash
# Check logs
sudo journalctl -u autoronto-dashboard -n 50

# Or
tail -50 ~/Autoronto/dashboard/logs/dashboard.error.log

# Common issues:
# - Python packages not installed: pip install -r requirements.txt
# - Wrong paths in service file
# - Permission issues: check file ownership
```

### **Can't Access from Network**:
```bash
# Verify dashboard is listening on 0.0.0.0
sudo netstat -tulpn | grep 8501

# Should show: 0.0.0.0:8501

# Check firewall
sudo ufw status
# OR
sudo firewall-cmd --list-ports

# Verify DNS
ping pm.in.autoronto.ca
```

### **Data Not Loading**:
```bash
# Check data files exist
ls -lh ~/Autoronto/data/

# Check config.json
cat ~/Autoronto/dashboard/config.json | grep data_source

# If "live", verify .env file exists
cat ~/Autoronto/.env
```

---

## 📊 Performance Optimization (Optional)

### **Install Watchdog for faster reload**:
```bash
source .venv/bin/activate
pip install watchdog
```

### **Set Resource Limits** (if needed):
Edit service file:
```ini
[Service]
MemoryLimit=2G
CPUQuota=200%
```

---

## 🎯 Quick Reference Commands

| Action | Command |
|--------|---------|
| Start service | `sudo systemctl start autoronto-dashboard` |
| Stop service | `sudo systemctl stop autoronto-dashboard` |
| Restart service | `sudo systemctl restart autoronto-dashboard` |
| Check status | `sudo systemctl status autoronto-dashboard` |
| View logs | `sudo journalctl -u autoronto-dashboard -f` |
| Enable on boot | `sudo systemctl enable autoronto-dashboard` |
| Disable on boot | `sudo systemctl disable autoronto-dashboard` |
| Test manually | `cd dashboard && streamlit run app.py` |

---

## 📁 Expected File Structure on Linux

```
/home/user/Autoronto/
├── .venv/                        # Created by setup
├── .env                          # Optional, for API
├── .gitignore
├── dashboard/
│   ├── .streamlit/
│   │   └── config.toml
│   ├── app.py
│   ├── config.json
│   ├── requirements.txt
│   ├── setup-linux.sh
│   ├── logs/                     # Created by setup
│   ├── pages/
│   ├── utils/
│   └── components/
└── data/
    ├── children_hierarchical_4336931.json
    ├── children_flat_4336931.json
    └── project_4336931.json
```

---

## 🎉 You're Done!

Dashboard should now be:
- ✅ Running on PC4 (Linux)
- ✅ Accessible at `http://pm.in.autoronto.ca:8501`
- ✅ Starting automatically on boot
- ✅ Restarting automatically if it crashes
- ✅ Logging to files for debugging

**Ready for Feb 17 Winter Workshop! 🏁**
