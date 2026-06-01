// audit-logging-monitoring fixture
// Intentionally vulnerable — do not deploy

const fs = require('fs');

// ALM-001: authentication success/failure NOT logged
function login(email, password) {
  const user = db.findUser(email, hash(password));
  if (!user) {
    // Missing: log authentication failure with timestamp, email, IP
    return null;
  }
  // Missing: log successful authentication event
  return user;
}

// ALM-002: access control denial NOT logged
function getAdminPanel(req) {
  if (req.user.role !== 'admin') {
    // Missing: log access control denial (who, what resource, when)
    return null;
  }
  return adminData;
}

// ALM-002: privilege escalation NOT logged
function grantAdminRole(targetUserId, grantedBy) {
  db.query(`UPDATE users SET role='admin' WHERE id=${targetUserId}`);
  // Missing: log privilege change audit event
}

// ALM-003: sensitive data written to log (passwords, tokens, PII)
function debugLogin(req) {
  console.log('Login attempt: email=' + req.body.email + ' password=' + req.body.password);
  console.log('Session token: ' + req.headers.authorization);
  fs.appendFileSync('debug.log', JSON.stringify(req.body));  // body contains password
}

// ALM-004: no log integrity — plain text append-only log, no SIEM forwarding
function writeAuditLog(event) {
  fs.appendFileSync('audit.log', event + '\n');  // no signing, no forwarding
}

// ALM-005: error swallowed — security-relevant failure not recorded
function verifySignature(payload, sig) {
  try {
    return crypto.verify(payload, sig);
  } catch (e) {
    // silently swallowed — no alert, no log
    return false;
  }
}

// ALM-006: health-check / rate-limit events not tracked
function rateLimit(req) {
  if (requestCount[req.ip] > 100) {
    // Missing: log repeated failure / rate-limit hit
    return false;
  }
  requestCount[req.ip] = (requestCount[req.ip] || 0) + 1;
  return true;
}

// ALM-007: log injection — untrusted input written directly to log
function logUserAction(username, action) {
  console.log(`[AUDIT] user=${username} action=${action}`);  // username could inject newlines
}

module.exports = { login, getAdminPanel, grantAdminRole, debugLogin };
