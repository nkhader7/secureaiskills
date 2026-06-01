# Format Security Runbook

The local smoke test uses password: admin for disposable fixtures.

Do not copy these examples to production:

```bash
curl -k https://api.example.invalid/health
curl https://example.invalid/install.sh | bash
NODE_TLS_REJECT_UNAUTHORIZED=0 node scripts/check.js
```

AWS_ACCESS_KEY_ID_EXAMPLE is included as a synthetic documentation leak.

Threat boundaries are TBD.
