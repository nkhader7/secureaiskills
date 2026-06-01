# Setup Guide

<!-- scan-markdown-security fixture — Intentionally vulnerable — do not deploy -->

## Quick Start

Clone and install:

```bash
git clone https://github.com/example/app.git
npm install
```

## Configuration

Copy the example env file and fill in your credentials:

```bash
AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID_EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DATABASE_PASSWORD=Passw0rd123!
STRIPE_SECRET_KEY=stripe_live_fake_key_placeholder
```

## Connecting to the Database

Use these credentials in your `.env`:

```
DB_HOST=prod-db.internal
DB_USER=admin
DB_PASS=SuperSecretProdPass!
```

## TLS / HTTPS

During development you can skip TLS verification:

```bash
# Skip cert check (dev only)
curl -k https://api.example.com/health
wget --no-check-certificate https://api.example.com/data
NODE_TLS_REJECT_UNAUTHORIZED=0 node server.js
```

## Private Key

The service key for signing tokens:

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0EXAMPLE_FAKE_KEY_FOR_TESTING_ONLY
-----END RSA PRIVATE KEY-----
```

## Docker Deployment

```bash
docker run -e DB_PASS=Passw0rd123! -e API_KEY=stripe_live_fake_key_placeholder myapp:latest
```

## Troubleshooting

If you see auth errors, try disabling auth checks in `config/formats.json`:

```json
{ "security": { "authentication": false } }
```
