# aUToronto PM Dashboard - Quick Start for Developers

> **TL;DR**: Streamlit dashboard running on PC4 (Linux) as a systemd service, accessible at `http://pm.in.autoronto.ca:8501` via VPN.

---

## 🎯 What You Need to Know

### Current Deployment

- **Host**: PC4 (`pc4.in.autoronto.ca` / `10.10.2.4`)
- **Access**: `http://pm.in.autoronto.ca:8501` (requires VPN)
- **Tech**: Python 3.8 + Streamlit + systemd
- **Location**: `/home/autoronto/Desktop/PM_Server/Autoronto/`
- **Service**: `autoronto-dashboard.service` (auto-starts on boot)

---

## 🚀 Quick Commands

### Managing the Service

```bash
# SSH into PC4
ssh autoronto@pc4.in.autoronto.ca

# Check status
sudo systemctl status autoronto-dashboard

# Restart
sudo systemctl restart autoronto-dashboard

# View logs
sudo journalctl -u autoronto-dashboard -f

# Stop/Start
sudo systemctl stop autoronto-dashboard
sudo systemctl start autoronto-dashboard
```

### Updating Code

```bash
# From your dev machine:
cd ~/Desktop/Uoft\ Studying/Autoronto/
rsync -avz --exclude='.venv' --exclude='data' \
  ./ autoronto@pc4.in.autoronto.ca:/home/autoronto/Desktop/PM_Server/Autoronto/

# Then restart on PC4:
ssh autoronto@pc4.in.autoronto.ca "sudo systemctl restart autoronto-dashboard"
```

### Manual Testing

```bash
# SSH into PC4
ssh autoronto@pc4.in.autoronto.ca
cd ~/Desktop/PM_Server/Autoronto/dashboard
source ../.venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
# Ctrl+C to stop
```

---

## 📁 Important Files

| File/Directory | Purpose |
|----------------|---------|
| `dashboard/app.py` | Main Streamlit entry point |
| `dashboard/config.json` | Dashboard configuration |
| `dashboard/pages/` | Dashboard pages (p1-p11) |
| `.env` | API credentials (NOT in git) |
| `.venv/` | Python virtual environment |
| `data/` | TeamGantt API cache |
| `/etc/systemd/system/autoronto-dashboard.service` | Systemd service file |

---

## 🔧 Common Tasks

### Update Dependencies

```bash
ssh autoronto@pc4.in.autoronto.ca
cd ~/Desktop/PM_Server/Autoronto
source .venv/bin/activate
pip install -r dashboard/requirements.txt
sudo systemctl restart autoronto-dashboard
```

### Clear Data Cache

```bash
ssh autoronto@pc4.in.autoronto.ca
cd ~/Desktop/PM_Server/Autoronto
rm -rf data/*.json data/*.csv
sudo systemctl restart autoronto-dashboard
```

### Update API Credentials

```bash
ssh autoronto@pc4.in.autoronto.ca
nano ~/Desktop/PM_Server/Autoronto/.env
# Edit credentials
sudo systemctl restart autoronto-dashboard
```

### Check Resource Usage

```bash
ssh autoronto@pc4.in.autoronto.ca
htop  # Overall system
ps aux | grep streamlit  # Dashboard process
df -h  # Disk space
```

---

## 🐛 Troubleshooting

### Dashboard won't start?

```bash
# Check logs
sudo journalctl -u autoronto-dashboard -n 50

# Common issues:
# 1. Missing .env → Create it with API credentials
# 2. Port in use → sudo netstat -tulpn | grep 8501
# 3. Bad venv → rm -rf .venv && ./dashboard/setup-linux.sh
```

### Can't access from browser?

```bash
# Check service is running
sudo systemctl status autoronto-dashboard

# Test local access
curl http://localhost:8501

# Verify VPN connection
ping 10.10.2.4

# Check DNS
ping pm.in.autoronto.ca  # Should resolve to 10.10.2.4
```

### Pages are blank?

```bash
# Usually API credential issue
sudo journalctl -u autoronto-dashboard | grep -i error

# Or cache corruption
rm -rf ~/Desktop/PM_Server/Autoronto/data/*.json
sudo systemctl restart autoronto-dashboard
```

---

## 🎨 Development Workflow

1. **Make changes locally** on your dev machine (macOS/Linux)
2. **Test locally**: `streamlit run dashboard/app.py`
3. **Transfer to PC4**: Use `rsync` command above
4. **Restart service**: `ssh ... sudo systemctl restart autoronto-dashboard`
5. **Verify**: Check `http://pm.in.autoronto.ca:8501` in browser

---

## 📖 Full Documentation

- **`DEPLOYMENT_GUIDE.md`** - Complete deployment documentation (this workflow)
- **`NGINX_SETUP_GUIDE.md`** - How to remove `:8501` from URL
- **`LINUX_SETUP_GUIDE.md`** - Detailed Linux setup steps
- **`DASHBOARD_REQUIREMENTS.md`** - Feature requirements & design decisions

---

## ⚡ Architecture Overview

```
[Browser on VPN] 
    ↓
[pm.in.autoronto.ca:8501] (via PiHole DNS)
    ↓
[PC4: 10.10.2.4:8501]
    ↓
[Systemd Service: autoronto-dashboard]
    ↓
[Streamlit App in .venv]
    ↓
[TeamGantt API + Local Cache]
```

---

## 🔐 Security Notes

- **`.env` file**: Contains API credentials, NEVER commit to git
- **VPN required**: Dashboard only accessible on internal network
- **Port 8501**: Open on PC4 firewall for internal access
- **Credentials**: Stored in `/home/autoronto/Desktop/PM_Server/Autoronto/.env`

---

## 🚀 Next Steps (Optional)

### Remove port from URL:

Install Nginx reverse proxy to access at `http://pm.in.autoronto.ca` (without `:8501`)

See: **`NGINX_SETUP_GUIDE.md`**

Quick version:
```bash
sudo apt install nginx
# Configure reverse proxy (see guide)
sudo systemctl reload nginx
```

---

**Questions?** See `DEPLOYMENT_GUIDE.md` for detailed explanations.

**Access**: `http://pm.in.autoronto.ca:8501` (VPN required)  
**Status**: ✅ Production Ready  
**Last Updated**: Feb 14, 2026
