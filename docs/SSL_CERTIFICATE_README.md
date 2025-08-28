# SSL Certificate Files

This directory contains SSL certificate files generated for the N8N Security Integration project.

## Files Created

### `server.key` (Private Key)
- **Type**: RSA 2048-bit private key
- **Permissions**: 600 (read/write for owner only)
- **Usage**: Server-side SSL/TLS encryption
- **Security**: Keep this file secure and never share it

### `server.crt` (Certificate)
- **Type**: Self-signed X.509 certificate
- **Validity**: 365 days from creation date
- **Subject**: `/C=US/ST=State/L=City/O=N8N-Sec/OU=Security/CN=localhost`
- **Usage**: Public certificate for SSL/TLS connections

### `server.pem` (Combined File)
- **Type**: Combined certificate and private key in PEM format
- **Usage**: Some applications prefer this combined format
- **Contains**: Both certificate and private key in one file

## Usage Examples

### For N8N HTTPS Configuration
```yaml
# In docker-compose.yml or N8N configuration
N8N_PROTOCOL: https
N8N_SSL_KEY: /path/to/server.key
N8N_SSL_CERT: /path/to/server.crt
```

### For Nginx SSL Configuration
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/server.crt;
    ssl_certificate_key /path/to/server.key;
    # ... other configuration
}
```

### For Apache SSL Configuration
```apache
SSLEngine on
SSLCertificateFile /path/to/server.crt
SSLCertificateKeyFile /path/to/server.key
```

## Security Notes

1. **Self-Signed Certificate**: This is a self-signed certificate suitable for development and testing. For production, use a certificate from a trusted Certificate Authority (CA).

2. **Private Key Security**: The `server.key` file contains sensitive cryptographic material. Ensure proper file permissions (600) and never commit it to version control.

3. **Certificate Validation**: Browsers will show security warnings for self-signed certificates. This is expected behavior.

4. **Renewal**: The certificate is valid for 365 days. Set up a renewal process before expiration.

## Regenerating Certificates

To create new certificates:

```bash
# Generate new private key
openssl genrsa -out server.key 2048

# Generate new self-signed certificate
openssl req -new -x509 -key server.key -out server.crt -days 365 \
  -subj "/C=US/ST=State/L=City/O=N8N-Sec/OU=Security/CN=localhost"

# Create combined PEM file
cat server.crt server.key > server.pem
```

## Integration with Project

These SSL certificates can be used to secure:
- N8N web interface (HTTPS)
- Webhook endpoints
- API communications
- Inter-service communications in the Docker environment

For the Wazuh integration, ensure that SSL certificates are properly configured if using HTTPS endpoints for webhook communications.