# AI NutriCare System - Security Guide

## Overview

This document outlines the security measures implemented in the AI NutriCare System and best practices for secure deployment.

## Security Features

### 1. Data Encryption

#### Encryption at Rest
- **Algorithm**: AES-256-GCM
- **Encrypted Fields**:
  - Patient names
  - Medical report content
  - Doctor's notes
  - Diet plan details
- **Key Management**:
  - Keys stored in environment variables
  - Never committed to version control
  - Rotation supported

#### Encryption in Transit
- TLS 1.2+ for all network communications
- Certificate validation enabled
- Secure API connections (HTTPS only)

### 2. Input Validation and Sanitization

#### File Upload Security
- **Allowed Formats**: PDF, JPEG, PNG, TIFF, TXT only
- **Size Limit**: 10MB maximum
- **Path Traversal Protection**: Filename sanitization
- **Content Validation**: Magic byte verification

#### Text Input Sanitization
- XSS prevention (script tag removal)
- SQL injection prevention (parameterized queries)
- Null byte filtering
- Length limits enforced

### 3. Authentication and Authorization

#### API Key Authentication
- SHA-256 hashed keys
- Secure key generation
- Key rotation support
- Per-endpoint authentication

#### Rate Limiting
- Default: 100 requests per hour per identifier
- Configurable limits
- Automatic blocking of excessive requests
- Reset time tracking

### 4. Audit Logging

All security-relevant events are logged:
- User authentication attempts
- Data access (read/write/delete)
- Configuration changes
- Error conditions
- API calls

Log format:
```json
{
  "timestamp": "2026-02-15T10:30:00Z",
  "action": "data_access",
  "patient_id": "P123456",
  "user": "user@example.com",
  "ip_address": "192.168.1.1",
  "success": true
}
```

### 5. Security Headers

All HTTP responses include:
- `X-Frame-Options: DENY` - Prevent clickjacking
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `X-XSS-Protection: 1; mode=block` - Enable XSS protection
- `Strict-Transport-Security` - Force HTTPS
- `Content-Security-Policy` - Restrict resource loading
- `Referrer-Policy` - Control referrer information

### 6. CORS Configuration

- Whitelist-based origin validation
- Configurable allowed methods and headers
- Preflight request caching
- Default: localhost only

---

## Threat Model

### Threats Addressed

1. **Unauthorized Data Access**
   - Mitigation: Encryption at rest, authentication, audit logging

2. **Data Breach**
   - Mitigation: Encryption, secure key management, TLS

3. **Injection Attacks (SQL, XSS)**
   - Mitigation: Input sanitization, parameterized queries, CSP headers

4. **Denial of Service**
   - Mitigation: Rate limiting, input validation, resource limits

5. **Man-in-the-Middle Attacks**
   - Mitigation: TLS, certificate validation, HSTS

6. **Malicious File Upload**
   - Mitigation: File type validation, size limits, content scanning

### Known Limitations

1. **Local Storage**: SQLite database is stored locally. For production, use PostgreSQL with proper access controls.

2. **API Key Storage**: API keys stored in environment variables. For production, use a secrets management service (e.g., AWS Secrets Manager, HashiCorp Vault).

3. **No User Authentication**: Current version doesn't have user login. Implement OAuth2/OIDC for multi-user deployments.

4. **Limited Malware Scanning**: Basic file validation only. Consider integrating antivirus scanning for production.

---

## Security Best Practices

### Deployment

1. **Use HTTPS Only**
   ```bash
   # Configure reverse proxy (nginx example)
   server {
       listen 443 ssl http2;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
   }
   ```

2. **Secure Environment Variables**
   ```bash
   # Use secrets management
   export OPENAI_API_KEY=$(aws secretsmanager get-secret-value --secret-id openai-key --query SecretString --output text)
   ```

3. **Database Security**
   ```python
   # Use PostgreSQL with SSL
   store = DataStore(
       db_type="postgresql",
       db_config={
           'host': 'db.example.com',
           'sslmode': 'require',
           'sslcert': '/path/to/client-cert.pem',
           'sslkey': '/path/to/client-key.pem',
           'sslrootcert': '/path/to/ca-cert.pem'
       }
   )
   ```

4. **Regular Updates**
   ```bash
   # Keep dependencies updated
   pip install --upgrade -r requirements.txt
   
   # Check for vulnerabilities
   pip install safety
   safety check
   ```

### Key Management

1. **Generate Strong Keys**
   ```python
   import secrets
   
   # Encryption key (32 bytes)
   encryption_key = secrets.token_hex(16)
   
   # API key (256 bits)
   api_key = secrets.token_urlsafe(32)
   ```

2. **Rotate Keys Regularly**
   ```python
   # Rotate encryption key
   store.rotate_encryption_key(
       old_key=os.getenv('OLD_KEY'),
       new_key=os.getenv('NEW_KEY')
   )
   ```

3. **Never Commit Keys**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.key" >> .gitignore
   echo "*.pem" >> .gitignore
   ```

### Access Control

1. **Principle of Least Privilege**
   - Grant minimum necessary permissions
   - Use separate accounts for different services
   - Limit database user permissions

2. **Network Segmentation**
   - Isolate database from public network
   - Use firewall rules
   - VPN for remote access

3. **Monitoring and Alerting**
   ```python
   # Set up alerts for suspicious activity
   if failed_login_attempts > 5:
       send_alert("Multiple failed login attempts")
   
   if data_access_after_hours:
       send_alert("Unusual access time")
   ```

### Data Protection

1. **Backup Encryption**
   ```bash
   # Encrypt backups
   gpg --symmetric --cipher-algo AES256 backup.db
   ```

2. **Secure Deletion**
   ```python
   # Verify deletion
   result = store.delete_patient_data(patient_id)
   assert result == True
   
   # Audit log entry created automatically
   ```

3. **Data Retention**
   ```python
   # Implement retention policy
   def cleanup_old_data(days=365):
       cutoff = datetime.now() - timedelta(days=days)
       store.delete_records_before(cutoff)
   ```

---

## Compliance Considerations

### HIPAA (Health Insurance Portability and Accountability Act)

For HIPAA compliance, additional measures required:

1. **Business Associate Agreement (BAA)**
   - Required with all third-party services (OpenAI, USDA)
   - Ensure vendors are HIPAA-compliant

2. **Access Controls**
   - Implement user authentication
   - Role-based access control (RBAC)
   - Unique user identification

3. **Audit Controls**
   - Enhanced audit logging
   - Log retention (6 years minimum)
   - Regular audit reviews

4. **Transmission Security**
   - End-to-end encryption
   - Secure messaging
   - VPN for remote access

5. **Physical Safeguards**
   - Secure server location
   - Access controls to facilities
   - Workstation security

### GDPR (General Data Protection Regulation)

For GDPR compliance:

1. **Data Minimization**
   - Collect only necessary data
   - Implement data retention limits
   - Regular data cleanup

2. **Right to Access**
   - Provide data export functionality
   - JSON export available

3. **Right to Erasure**
   - Complete data deletion implemented
   - Verification of deletion

4. **Data Portability**
   - Export in machine-readable format (JSON)
   - Easy data transfer

5. **Privacy by Design**
   - Encryption by default
   - Minimal data collection
   - Secure defaults

---

## Incident Response

### Security Incident Procedure

1. **Detection**
   - Monitor logs for anomalies
   - Set up automated alerts
   - Regular security audits

2. **Containment**
   ```bash
   # Immediately revoke compromised keys
   # Disable affected accounts
   # Isolate affected systems
   ```

3. **Investigation**
   - Review audit logs
   - Identify scope of breach
   - Document findings

4. **Recovery**
   - Restore from clean backups
   - Rotate all keys
   - Apply security patches

5. **Post-Incident**
   - Update security measures
   - Notify affected parties
   - Document lessons learned

### Contact Information

For security issues:
- Email: security@example.com
- PGP Key: [Public key fingerprint]

---

## Security Checklist

### Pre-Deployment

- [ ] All API keys configured in environment variables
- [ ] Encryption key generated and secured
- [ ] TLS certificates obtained and configured
- [ ] Database access controls configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation tested

### Post-Deployment

- [ ] Security scan completed
- [ ] Penetration testing performed
- [ ] Audit logging verified
- [ ] Backup restoration tested
- [ ] Incident response plan documented
- [ ] Team trained on security procedures
- [ ] Compliance requirements verified
- [ ] Regular security reviews scheduled

### Ongoing

- [ ] Weekly: Review audit logs
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Rotate encryption keys
- [ ] Quarterly: Security audit
- [ ] Annually: Penetration testing
- [ ] Annually: Compliance review

---

## Security Tools

### Recommended Tools

1. **Dependency Scanning**
   ```bash
   pip install safety
   safety check
   ```

2. **Static Analysis**
   ```bash
   pip install bandit
   bandit -r ai_diet_planner/
   ```

3. **Secret Scanning**
   ```bash
   pip install detect-secrets
   detect-secrets scan
   ```

4. **Vulnerability Scanning**
   ```bash
   pip install pip-audit
   pip-audit
   ```

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [GDPR](https://gdpr.eu/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

## Updates

This security guide should be reviewed and updated:
- When new features are added
- After security incidents
- When compliance requirements change
- At least annually

Last Updated: 2026-02-15
