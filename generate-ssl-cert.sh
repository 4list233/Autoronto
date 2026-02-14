#!/bin/bash
# Generate self-signed SSL certificate for internal use

echo "Generating self-signed SSL certificate for pm.in.autoronto.ca"
echo ""

# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate certificate (valid for 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/pm.autoronto.key \
  -out /etc/nginx/ssl/pm.autoronto.crt \
  -subj "/C=CA/ST=Ontario/L=Toronto/O=University of Toronto/OU=aUToronto/CN=pm.in.autoronto.ca"

# Set permissions
sudo chmod 600 /etc/nginx/ssl/pm.autoronto.key
sudo chmod 644 /etc/nginx/ssl/pm.autoronto.crt

echo ""
echo "✓ SSL certificate created!"
echo ""
echo "Next steps:"
echo "1. Copy nginx-pm-dashboard-ssl.conf to /etc/nginx/sites-available/pm-dashboard"
echo "2. Enable site: sudo ln -s /etc/nginx/sites-available/pm-dashboard /etc/nginx/sites-enabled/"
echo "3. Test config: sudo nginx -t"
echo "4. Reload nginx: sudo systemctl reload nginx"
echo "5. Allow HTTPS: sudo ufw allow 443/tcp"
echo ""
echo "Access at: https://pm.in.autoronto.ca (ignore browser warning for self-signed cert)"
