# SAFE FIXTURE — scan-for-ssrf test
# URL validation with allowlist — SSRF risk is mitigated.
# NOTE: request.args still appears here; the SSRF patterns will match the parameter read.
# The LLM evaluation layer (not regex) determines whether the validation is sufficient.
# This fixture demonstrates the CORRECT pattern: read → validate → fetch.

import ipaddress
import urllib.parse
import requests

ALLOWED_HOSTS = frozenset({"api.example.com", "cdn.example.com", "data.example.com"})
ALLOWED_SCHEMES = frozenset({"https"})


def is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        pass
    return True


def safe_fetch(validated_url: str) -> str:
    """Only called after is_safe_url returns True."""
    return requests.get(validated_url, timeout=5).text
