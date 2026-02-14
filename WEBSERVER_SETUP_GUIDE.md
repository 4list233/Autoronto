# Web Server Setup Guide
## Hosting PM Dashboard at pm.in.autoronto.ca

This guide will help you set up the aUToronto PM Dashboard as a web service accessible via your internal DNS.

---

## 📋 Prerequisites

- ✅ PC4 has a static IP address
- ✅ PiHole DNS server is configured
- ✅ VPN is set up for team access
- ✅ PC4 is accessible at `pc4.in.autoronto.ca`

---

## 🔧 Setup Steps

### 1. Configure PiHole DNS

**On your PiHole admin panel:**

1. Navigate to **Local DNS** → **DNS Records**
2. Click **Add a new domain/IP combination**
3. Enter:
   - **Domain**: `pm.in.autoronto.ca`
   - **IP Address**: `<PC4's static IP>` (same IP as pc4.in.autoronto.ca)
4. Click **Add**

**Verify DNS works:**
```bash
# From any VPN-connected device
ping pm.in.autoronto.ca
# Should show PC4's IP address
```

---

### 2. Configure Firewall (macOS)

**Allow incoming connections on port 8501:**

1. Open **System Settings** → **Network** → **Firewall**
2. If Firewall is off, turn it on
3. Click **Options**
4. Click the **+** button to add an application
5. Navigate to: `/Users/5425855/Desktop/Uoft Studying/Autoronto/.venv/bin/streamlit`
6. Select it and click **Add**
7. Ensure it's set to **Allow incoming connections**

---

### 3. Start the Dashboard

You have **three options** to run the dashboard:

#### **Option A: Quick Start (Manual)**

Use this for testing or temporary access:

```bash
cd "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard"
./start-dashboard.sh
```

- Access at: **http://pm.in.autoronto.ca:8501**
- Press `Ctrl+C` to stop
- Dashboard stops when terminal closes

---

#### **Option B: Background Process (Recommended for Development)**

```bash
cd "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard"
source ../.venv/bin/activate
nohup streamlit run app.py --server.address=0.0.0.0 --server.port=8501 > logs/dashboard.log 2>&1 &
```

**To stop:**
```bash
pkill -f "streamlit run app.py"
```

**To check if running:**
```bash
ps aux | grep streamlit
```

**To view logs:**
```bash
tail -f "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard/logs/dashboard.log"
```

---

#### **Option C: System Service (Recommended for Production)**

This makes the dashboard start automatically on boot and restart if it crashes.

**Setup (one-time):**
```bash
# Copy the service file to LaunchAgents
cp "/Users/5425855/Desktop/Uoft Studying/Autoronto/ca.autoronto.pm-dashboard.plist" \
   ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/ca.autoronto.pm-dashboard.plist

# Start the service
launchctl start ca.autoronto.pm-dashboard
```

**Managing the service:**
```bash
# Check status
launchctl list | grep autoronto

# Stop service
launchctl stop ca.autoronto.pm-dashboard

# Start service
launchctl start ca.autoronto.pm-dashboard

# Restart service
launchctl stop ca.autoronto.pm-dashboard && launchctl start ca.autoronto.pm-dashboard

# Disable service (won't start on boot)
launchctl unload ~/Library/LaunchAgents/ca.autoronto.pm-dashboard.plist

# Enable service (will start on boot)
launchctl load ~/Library/LaunchAgents/ca.autoronto.pm-dashboard.plist

# View logs
tail -f "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard/logs/dashboard.log"
tail -f "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard/logs/dashboard.error.log"
```

---

## 🌐 Accessing the Dashboard

### From VPN-Connected Devices:

**URL**: `http://pm.in.autoronto.ca:8501`

### Troubleshooting Access:

1. **Can't resolve pm.in.autoronto.ca?**
   - Check PiHole DNS configuration
   - Verify device is using PiHole as DNS server
   - Try: `nslookup pm.in.autoronto.ca`

2. **DNS resolves but can't connect?**
   - Verify dashboard is running: `ps aux | grep streamlit`
   - Check firewall settings on PC4
   - Verify port 8501 is not blocked

3. **Connection refused?**
   - Check if Streamlit is listening on 0.0.0.0: `netstat -an | grep 8501`
   - Verify `.streamlit/config.toml` has `address = "0.0.0.0"`

---

## 📊 Configuration Files

### Streamlit Config
Location: `dashboard/.streamlit/config.toml`

Key settings:
- `address = "0.0.0.0"` - Listen on all network interfaces
- `port = 8501` - Port number
- `serverAddress = "pm.in.autoronto.ca"` - Display this URL to users

### Dashboard Config
Location: `dashboard/config.json`

Key settings:
- `"data_source": "cached"` - Use local data (faster, no API calls)
- `"data_source": "live"` - Fetch from TeamGantt API (requires .env with API token)

---

## 🔒 Security Considerations

1. **VPN Only**: Dashboard should only be accessible via VPN
2. **No Public Internet**: Ensure PC4's firewall blocks port 8501 from public internet
3. **TeamGantt API**: If using "live" data source, protect .env file with API credentials
4. **User Access**: Consider implementing Streamlit authentication if needed

---

## 📈 Monitoring

### Check Dashboard Status:
```bash
curl http://pm.in.autoronto.ca:8501
```

### View Real-Time Logs:
```bash
tail -f "/Users/5425855/Desktop/Uoft Studying/Autoronto/dashboard/logs/dashboard.log"
```

### Check Resource Usage:
```bash
ps aux | grep streamlit
top -pid $(pgrep -f "streamlit run app.py")
```

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Quick start | `./start-dashboard.sh` |
| Start service | `launchctl start ca.autoronto.pm-dashboard` |
| Stop service | `launchctl stop ca.autoronto.pm-dashboard` |
| View logs | `tail -f dashboard/logs/dashboard.log` |
| Check if running | `ps aux \| grep streamlit` |
| Kill process | `pkill -f "streamlit run app.py"` |
| Access dashboard | http://pm.in.autoronto.ca:8501 |

---

## 📞 Support

For issues or questions:
1. Check logs: `dashboard/logs/dashboard.error.log`
2. Verify DNS: `ping pm.in.autoronto.ca`
3. Test locally first: `http://localhost:8501`
4. Check firewall and network settings

---

**Dashboard is now ready for your Feb 17 Winter Workshop! 🎉**
