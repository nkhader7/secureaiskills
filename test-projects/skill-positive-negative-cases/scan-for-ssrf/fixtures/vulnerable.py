# VULNERABLE FIXTURE — scan-for-ssrf test

import requests

# SSRF-001: User-controlled URL fetched directly
def fetch_url(request):
    url = request.args.get("url")
    return requests.get(url).text

# SSRF-002: IMDS metadata endpoint access
def get_aws_role():
    resp = requests.get("http://169.254.169.254/latest/meta-data/iam/security-credentials/")
    return resp.json()

# SSRF-003: localhost access
def health_check(request):
    target = request.args.get("host", "localhost")
    return requests.get(f"http://localhost:8080/health").text

# SSRF-004: URL from user input concatenated
def proxy(request):
    base = "https://internal-api.company.com/"
    path = request.params.get("path")
    url = base + path
    return requests.get(url).json()
