# Deployment Guide

This guide covers deploying the Phone Tracking System to production.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ (recommended for production)
- SSL certificate for HTTPS
- Server with sufficient resources (2GB RAM minimum)
- OpenCellID API key (for BTS triangulation)

## Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib

# Install system packages
sudo apt install -y build-essential libpq-dev
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql

CREATE DATABASE tracking_db;
CREATE USER tracking_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE tracking_db TO tracking_user;
\q
```

### 3. Application Setup

```bash
# Clone repository
cd /opt
git clone <repository-url> phone-tracking
cd phone-tracking

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 4. Environment Configuration

Create production `.env` file:

```bash
cp .env.example .env
nano .env
```

Configure with production values:

```env
# Flask Configuration
SECRET_KEY=<generate-with-scripts/generate_keys.py>
FLASK_ENV=production
FLASK_DEBUG=False
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=postgresql://tracking_user:secure_password@localhost:5432/tracking_db

# OpenCellID
OPENCELLID_API_KEY=<your-api-key>

# Security
JWT_SECRET=<generate-with-scripts/generate_keys.py>
ENCRYPTION_KEY=<generate-with-scripts/generate_keys.py>

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=5

# Token Expiration
TOKEN_EXPIRATION_HOURS=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/phone-tracking/tracking.log
```

### 5. Generate Security Keys

```bash
python scripts/generate_keys.py
```

Copy the generated keys to your `.env` file.

### 6. Initialize Database

```bash
python init_db.py
```

### 7. Create Systemd Service

Create `/etc/systemd/system/phone-tracking.service`:

```ini
[Unit]
Description=Phone Tracking System
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/phone-tracking
Environment="PATH=/opt/phone-tracking/venv/bin"
ExecStart=/opt/phone-tracking/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/phone-tracking/access.log \
    --error-logfile /var/log/phone-tracking/error.log \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. Configure Nginx

Create `/etc/nginx/sites-available/phone-tracking`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /opt/phone-tracking/static;
        expires 30d;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/phone-tracking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 10. Set Up Logging

```bash
sudo mkdir -p /var/log/phone-tracking
sudo chown www-data:www-data /var/log/phone-tracking
```

### 11. Start Services

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable phone-tracking
sudo systemctl start phone-tracking

# Check status
sudo systemctl status phone-tracking

# View logs
sudo journalctl -u phone-tracking -f
```

## Security Hardening

### Firewall Configuration

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Database Security

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Change authentication method to md5
# host    all    all    127.0.0.1/32    md5

sudo systemctl restart postgresql
```

### File Permissions

```bash
sudo chown -R www-data:www-data /opt/phone-tracking
sudo chmod 600 /opt/phone-tracking/.env
```

## Monitoring

### Log Rotation

Create `/etc/logrotate.d/phone-tracking`:

```
/var/log/phone-tracking/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload phone-tracking > /dev/null 2>&1 || true
    endscript
}
```

### Health Checks

Create a cron job for health monitoring:

```bash
*/5 * * * * curl -f http://localhost:8000/ || systemctl restart phone-tracking
```

## Backup Strategy

### Database Backup

Create `/opt/phone-tracking/scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/phone-tracking"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U tracking_user tracking_db | \
    gzip > $BACKUP_DIR/tracking_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "tracking_db_*.sql.gz" -mtime +30 -delete
```

Schedule with cron:

```bash
0 2 * * * /opt/phone-tracking/scripts/backup_db.sh
```

## Scaling

### Horizontal Scaling

1. Use a load balancer (nginx, HAProxy)
2. Deploy multiple application instances
3. Use shared PostgreSQL database
4. Implement Redis for session storage

### Vertical Scaling

```bash
# Increase Gunicorn workers
# Rule of thumb: (2 x CPU cores) + 1
--workers 9  # for 4-core server
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u phone-tracking -n 50

# Check configuration
source venv/bin/activate
python app.py  # Test locally
```

### Database Connection Issues

```bash
# Test connection
psql -h localhost -U tracking_user -d tracking_db

# Check PostgreSQL status
sudo systemctl status postgresql
```

### High Memory Usage

```bash
# Reduce workers in systemd service
--workers 2

# Monitor resources
htop
```

## Maintenance

### Update Application

```bash
cd /opt/phone-tracking
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart phone-tracking
```

### Database Migrations

```bash
# Backup first
pg_dump tracking_db > backup.sql

# Run migrations
python migrate.py

# Test
python -c "from app import create_app; app = create_app(); app.app_context().push()"
```

## Performance Optimization

### Database Indexing

```sql
CREATE INDEX idx_location_logs_device_timestamp 
ON location_logs(device_id, timestamp DESC);

CREATE INDEX idx_remote_sessions_token 
ON remote_sessions(session_token);

CREATE INDEX idx_access_logs_session 
ON access_logs(session_id);
```

### Caching

Consider adding Redis for:
- Rate limiting storage
- Session caching
- Frequently accessed location data

## Compliance

### GDPR Compliance

1. Implement data deletion on request
2. Add data export functionality
3. Maintain consent records
4. Document data processing

### Audit Requirements

1. Enable comprehensive logging
2. Regular security audits
3. Penetration testing
4. Compliance reporting

## Support

For production issues:
1. Check logs first
2. Review systemd service status
3. Verify database connectivity
4. Check SSL certificate validity
5. Monitor resource usage

---

**Remember: Always test in a staging environment before deploying to production.**
