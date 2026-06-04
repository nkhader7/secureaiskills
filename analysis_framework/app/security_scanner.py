import re
from typing import Dict, List, Any

# Mapping of findings to standards
OWASP_LLM_TOP_10 = {
    "secret": "OWASP LLM-01: Prompt Injection (hardcoded secrets risk exposure)",
    "sast": "OWASP LLM-07: Unsafe Code Execution",
    "prompt_injection": "OWASP LLM-01: Prompt Injection",
    "dependency": "OWASP LLM-06: Supply Chain Vulnerabilities",
}

NIST_CATEGORIES = {
    "secret": ["ID.RA-1", "PR.AC-1"],
    "sast": ["PR.IP-1", "DE.CM-3"],
    "prompt_injection": ["ID.RA-1"],
    "dependency": ["SC.L1-3.14"],
}

CIS_CONTROLS = {
    "secret": ["CIS 1.1", "CIS 6.1"],
    "sast": ["CIS 1.1", "CIS 2.5"],
    "prompt_injection": ["CIS 3.1"],
    "dependency": ["CIS 3.10"],
}

CWE_MAPPING = {
    "eval_usage": "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code",
    "exec_usage": "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code",
    "os_system": "CWE-78: Improper Neutralization of Special Elements used in an OS Command",
    "subprocess_shell": "CWE-78: Improper Neutralization of Special Elements used in an OS Command",
    "aws_access_key": "CWE-798: Use of Hard-coded Credentials",
    "generic_api_key": "CWE-798: Use of Hard-coded Credentials",
}

# Simple regex-based secret detectors
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r'(?i)aws(.{0,20})?(secret|secret_access_key|secretkey)["\'=:\s]+([A-Za-z0-9/+=]{40})'),
    "generic_api_key": re.compile(r'(?i)(api[_-]?key|token)["\'=:\s]+[A-Za-z0-9\-_.]{8,64}'),
    "private_key_block": re.compile(r"-----BEGIN (?:RSA|PRIVATE|OPENSSH) PRIVATE KEY-----"),
}

SAST_PATTERNS = {
    "eval_usage": re.compile(r"\beval\s*\("),
    "exec_usage": re.compile(r"\bexec\s*\("),
    "os_system": re.compile(r"\bos\.system\s*\("),
    "subprocess_shell": re.compile(r"subprocess\.(?:Popen|run|call)\([^)]*shell\s*=\s*True"),
}

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (previous|above) instructions"),
    re.compile(r"(?i)disregard (previous|above)"),
    re.compile(r"(?i)follow these new instructions"),
]


def detect_secrets(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    for name, content in files.items():
        txt = content if isinstance(content, str) else ''
        for key, pat in SECRET_PATTERNS.items():
            for m in pat.finditer(txt):
                findings.append({
                    "file": name, "type": "secret", "subtype": key, "match": m.group(0)[:16] + "...",
                    "severity": "critical", "cwe": CWE_MAPPING.get(key),
                    "owasp_llm": OWASP_LLM_TOP_10.get("secret"),
                    "nist": NIST_CATEGORIES.get("secret"),
                    "cis": CIS_CONTROLS.get("secret"),
                })
    return findings


def detect_sast_issues(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    for name, content in files.items():
        txt = content if isinstance(content, str) else ''
        for key, pat in SAST_PATTERNS.items():
            if pat.search(txt):
                findings.append({
                    "file": name, "type": "sast", "subtype": key, "severity": "high",
                    "cwe": CWE_MAPPING.get(key),
                    "owasp_llm": OWASP_LLM_TOP_10.get("sast"),
                    "nist": NIST_CATEGORIES.get("sast"),
                    "cis": CIS_CONTROLS.get("sast"),
                })
    return findings


def detect_prompt_injection(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    for name, content in files.items():
        txt = content if isinstance(content, str) else ''
        for pat in PROMPT_INJECTION_PATTERNS:
            if pat.search(txt):
                findings.append({
                    "file": name, "type": "prompt_injection", "severity": "high",
                    "owasp_llm": OWASP_LLM_TOP_10.get("prompt_injection"),
                    "nist": NIST_CATEGORIES.get("prompt_injection"),
                    "cis": CIS_CONTROLS.get("prompt_injection"),
                })
    return findings


def detect_unpinned_dependencies(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    # Check for requirements.txt, pyproject.toml, Pipfile
    req = files.get('requirements.txt') or files.get('requirements')
    if req:
        for i, line in enumerate(req.splitlines(), start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # If no pinned version specifier
            if '==' not in line and '>=' not in line and '<=' not in line and '~=' not in line:
                findings.append({
                    "file": 'requirements.txt', "line": i, "type": 'dependency', "issue": 'unpinned_version',
                    "severity": 'medium', "text": line,
                    "owasp_llm": OWASP_LLM_TOP_10.get("dependency"),
                    "nist": NIST_CATEGORIES.get("dependency"),
                    "cis": CIS_CONTROLS.get("dependency"),
                })

    pyproj = files.get('pyproject.toml')
    if pyproj:
        # naive check for Poetry/PEP621 dependencies without version spec
        for line in pyproj.splitlines():
            if line.strip().startswith('name'):
                continue
            if '=' in line and '[' not in line:
                parts = line.split('=')
                if len(parts) == 2 and parts[1].strip().strip('"').strip() == '':
                    findings.append({
                        "file": 'pyproject.toml', "type": 'dependency', "issue": 'empty_spec', "severity": 'medium',
                        "text": line,
                        "owasp_llm": OWASP_LLM_TOP_10.get("dependency"),
                        "nist": NIST_CATEGORIES.get("dependency"),
                        "cis": CIS_CONTROLS.get("dependency"),
                    })

    return findings


def run_all_scanners(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings = []
    findings.extend(detect_secrets(files))
    findings.extend(detect_sast_issues(files))
    findings.extend(detect_prompt_injection(files))
    findings.extend(detect_unpinned_dependencies(files))
    return findings
