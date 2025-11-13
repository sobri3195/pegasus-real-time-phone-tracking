# Security Policy

## Overview

The Phone Tracking System implements multiple layers of security to protect sensitive location data and prevent unauthorized access.

## Security Features

### 1. Authentication & Authorization

#### JWT (JSON Web Tokens)
- **Algorithm**: HS256
- **Expiration**: 24 hours (configurable)
- **Claims**: device_id, issued_at, expiration, unique_id
- **Validation**: Signature verification on every request

#### Token Management
- Tokens stored in database with session tracking
- Automatic expiration enforcement
- Manual revocation capability
- IP address logging for audit trail

### 2. Encryption

#### Data in Transit
- **HTTPS/TLS**: Required in production
- **TLS Version**: 1.2 or higher
- **Cipher Suites**: Strong ciphers only

#### Data at Rest
- **Algorithm**: AES-256 via Fernet
- **Key Derivation**: PBKDF2 with SHA-256
- **Iterations**: 100,000
- **Salt**: Application-specific

### 3. Rate Limiting

Protects against abuse and DoS attacks:

- **Device Registration**: 10 requests/hour
- **Location Updates**: 120 requests/hour (2 per minute)
- **Remote Access Requests**: 5 requests/minute
- **General API**: 100 requests/hour

### 4. Input Validation

- All user inputs sanitized
- SQL injection prevention via SQLAlchemy ORM
- XSS protection on all outputs
- Type checking on all parameters

### 5. Audit Logging

Complete logging of:
- All remote access attempts
- Token generation and revocation
- Location updates
- Failed authentication attempts
- API endpoint access with IP addresses

## Threat Model

### Threats Addressed

1. **Unauthorized Access**
   - Mitigated by: JWT authentication, token expiration, IP logging

2. **Data Interception**
   - Mitigated by: HTTPS/TLS, AES-256 encryption

3. **Brute Force Attacks**
   - Mitigated by: Rate limiting, account lockout

4. **Session Hijacking**
   - Mitigated by: Short token lifetime, IP validation

5. **SQL Injection**
   - Mitigated by: ORM usage, parameterized queries

6. **DoS/DDoS**
   - Mitigated by: Rate limiting, connection limits

### Known Limitations

1. **BTS Location Accuracy**: BTS triangulation is less accurate than GPS (50-200m vs 3-5m)
2. **API Key Storage**: Environment variables should be secured
3. **Database Access**: Requires strong database credentials
4. **Physical Device Access**: Cannot prevent tracking if device is compromised

## Best Practices for Deployment

### 1. Environment Variables

```bash
# Never commit .env to version control
echo ".env" >> .gitignore

# Generate strong keys
python scripts/generate_keys.py

# Set restrictive file permissions
chmod 600 .env
```

### 2. Database Security

```sql
-- Use strong passwords
CREATE USER tracking_user WITH PASSWORD 'complex_random_password_here';

-- Limit permissions
GRANT SELECT, INSERT, UPDATE ON location_logs TO tracking_user;
GRANT SELECT, INSERT, UPDATE ON devices TO tracking_user;

-- Enable SSL for database connections
ALTER USER tracking_user SET ssl TO on;
```

### 3. Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 443/tcp  # HTTPS
ufw deny 5000/tcp  # Block direct Flask access
ufw enable
```

### 4. Nginx Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https:" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 5. Regular Updates

```bash
# Keep system updated
apt update && apt upgrade -y

# Update Python dependencies
pip list --outdated
pip install --upgrade package_name

# Monitor security advisories
# Subscribe to CVE notifications for dependencies
```

## Incident Response

### If a Security Breach Occurs

1. **Immediate Actions**
   ```bash
   # Revoke all active tokens
   UPDATE remote_sessions SET is_revoked = true;
   
   # Stop the service
   systemctl stop phone-tracking
   
   # Block all API access temporarily
   # Update nginx config or firewall
   ```

2. **Investigation**
   - Review access logs: `/var/log/phone-tracking/`
   - Check database audit logs
   - Analyze unusual patterns
   - Identify compromised accounts

3. **Remediation**
   - Patch vulnerabilities
   - Rotate all keys and secrets
   - Reset affected user accounts
   - Update security configurations

4. **Communication**
   - Notify affected users
   - Document incident
   - Report to authorities if required

## Reporting Security Vulnerabilities

### How to Report

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security concerns to: security@your-domain.com
2. Include detailed description and reproduction steps
3. Allow 48 hours for initial response
4. Coordinate disclosure timeline

### What We Commit To

- Acknowledge receipt within 48 hours
- Provide initial assessment within 5 business days
- Work on fix with priority based on severity
- Credit reporter (if desired) in security advisory
- Coordinate responsible disclosure

## Security Checklist for Operators

### Before Deployment

- [ ] Generated strong, unique keys for production
- [ ] Configured HTTPS with valid SSL certificate
- [ ] Set up firewall rules
- [ ] Configured database with strong passwords
- [ ] Enabled audit logging
- [ ] Reviewed and updated rate limits
- [ ] Set appropriate token expiration times
- [ ] Configured backup strategy
- [ ] Reviewed file permissions
- [ ] Disabled debug mode

### Regular Maintenance

- [ ] Review access logs weekly
- [ ] Check for failed authentication attempts
- [ ] Monitor rate limit violations
- [ ] Update dependencies monthly
- [ ] Rotate encryption keys quarterly
- [ ] Test backup restoration
- [ ] Review and update security policies
- [ ] Conduct security audits annually

### Monitoring Alerts

Set up alerts for:
- Multiple failed authentication attempts
- Unusual location data patterns
- Rate limit violations
- Database connection failures
- Disk space issues
- High CPU/memory usage
- SSL certificate expiration

## Compliance Considerations

### GDPR (European Union)

- Data minimization: Only collect necessary location data
- Right to access: API for users to retrieve their data
- Right to erasure: Implement data deletion
- Consent: Explicit consent verification built-in
- Data portability: Export functionality
- Breach notification: Report breaches within 72 hours

### CCPA (California)

- Disclosure: Clear privacy policy
- Opt-out: Allow users to stop tracking
- Data deletion: Honor deletion requests
- Non-discrimination: Equal service regardless of privacy choices

### Other Jurisdictions

Consult local legal counsel for:
- Data residency requirements
- Cross-border data transfer rules
- Surveillance and tracking laws
- Employee monitoring regulations
- Consent requirements

## Cryptographic Details

### Key Derivation

```python
# PBKDF2 Configuration
Algorithm: SHA-256
Iterations: 100,000
Salt: Application-specific (fixed)
Output: 32 bytes
```

### Encryption

```python
# Fernet (AES-128 CBC + HMAC)
Key Size: 256 bits (after base64 encoding)
Mode: CBC
Padding: PKCS7
Authentication: HMAC-SHA256
```

### Token Signing

```python
# JWT HS256
Algorithm: HMAC-SHA256
Key Size: 256 bits recommended
Header: {"alg": "HS256", "typ": "JWT"}
```

## Security Contact

For security-related inquiries:
- **Email**: security@your-domain.com
- **PGP Key**: [Provide PGP public key]
- **Response Time**: Within 48 hours

---

**Remember**: Security is a continuous process, not a one-time implementation. Regular reviews and updates are essential.
