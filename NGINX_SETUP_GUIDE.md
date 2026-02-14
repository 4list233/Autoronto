# Remove Port from URL - Nginx Reverse Proxy Setup

This guide shows how to access the dashboard at `http://pm.in.autoronto.ca` (without `:8501`)

---

## 🎯 Goal

**Before**: `http://pm.in.autoronto.ca:8501` ❌  
**After**: `http://pm.in.autoronto.ca` ✅

---

## 📦 Setup (On PC4)

### **Step 1: Install Nginx**

```bash
sudo apt update
sudo apt install nginx
```

### **Step 2: Create Nginx Configuration**

```bash
sudo nano /etc/nginx/sites-available/pm-dashboard
```

**Paste this content:**

```nginx
server {
    listen 80;
    server_name pm.in.autoronto.ca;

    # Increase timeouts for Streamlit
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        
        # WebSocket support (required for Streamlit)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Forward headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_stcore {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

### **Step 3: Enable the Site**

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/pm-dashboard /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
```

You should see: `syntax is ok` and `test is successful`

### **Step 4: Start/Reload Nginx**

```bash
# Enable nginx to start on boot
sudo systemctl enable nginx

# Reload nginx with new configuration
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

### **Step 5: Allow Port 80 in Firewall**

```bash
sudo ufw allow 80/tcp
```

---

## ✅ Test Access

### **From PC4:**
```bash
curl http://localhost
curl http://pm.in.autoronto.ca
```

Both should return HTML content.

### **From another VPN device:**

Open browser and go to:
- ✅ **`http://pm.in.autoronto.ca`** (no port!)
- ✅ **`http://10.10.2.4`** (direct IP, no port)

---

## 🔐 Optional: Add HTTPS

If you want to use `https://pm.in.autoronto.ca`:

```bash
# Generate self-signed certificate
cd ~/Desktop/PM_Server/Autoronto
./generate-ssl-cert.sh

# Use the SSL config instead
sudo cp nginx-pm-dashboard-ssl.conf /etc/nginx/sites-available/pm-dashboard

# Enable and reload
sudo ln -sf /etc/nginx/sites-available/pm-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Allow HTTPS port
sudo ufw allow 443/tcp
```

Access at: **`https://pm.in.autoronto.ca`** (browser will show security warning for self-signed cert, but it's safe for internal use)

---

## 🛠️ Troubleshooting

### **Port 80 already in use?**
```bash
sudo netstat -tulpn | grep :80
# If something else is using port 80, either:
# 1. Stop that service, OR
# 2. Use a different port (e.g., 8080) in nginx config
```

### **Nginx won't reload?**
```bash
sudo nginx -t  # Check for syntax errors
sudo journalctl -xe  # Check logs
```

### **Dashboard shows but styles are broken?**
This is usually a WebSocket issue. Make sure the nginx config includes the `Upgrade` and `Connection` headers.

---

## 📊 How It Works

```
Browser Request: http://pm.in.autoronto.ca
         ↓
    Nginx (port 80)
         ↓
    Streamlit (port 8501)
         ↓
    Dashboard renders
```

Nginx acts as a reverse proxy, forwarding requests from port 80 to port 8501 behind the scenes.

---

**Summary**: Install nginx, copy the config file, enable it, and you can access at `http://pm.in.autoronto.ca` without the port! 🚀
