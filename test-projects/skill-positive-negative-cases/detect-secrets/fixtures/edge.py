# EDGE CASE FIXTURE — detect-secrets
# Boundary cases: test values, partial patterns, and comments.

# Edge: clearly labelled test values — skill should still flag, LLM decides severity
TEST_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"  # noqa: S105 - test value

# Edge: base64 blob that LOOKS like a key but is not
SOME_CONFIG_BLOB = "dGVzdGtleXRlc3RrZXl0ZXN0a2V5"

# Edge: key in a comment (no assignment)
# Old key was: AKIAIOSFODNN7EXAMPLE - decommissioned 2024-01-01

# Edge: partial PRIVATE KEY marker in a multiline string
CERT_HEADER = "-----BEGIN CERTIFICATE-----"  # certificates are not private keys

# Edge: git URL with embedded token (DS patterns may catch this)
REPO_URL = "https://oauth2:glpat-ABCDEFGHIJKLMNOPQRST@gitlab.example.com/repo.git"
