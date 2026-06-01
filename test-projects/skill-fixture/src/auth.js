// audit-auth-session-management fixture
// Intentionally vulnerable — do not deploy

const crypto = require('crypto');
const jwt = require('jsonwebtoken');

// ASM-001: weak password hashing (MD5 instead of bcrypt/argon2)
function hashPassword(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}

// ASM-001: SHA1 also weak
function legacyHash(password) {
  return crypto.createHash('sha1').update(password).digest('hex');
}

// ASM-002: no MFA check before sensitive action
async function deleteAccount(userId) {
  // Missing: verify second factor before destructive action
  await db.query(`DELETE FROM users WHERE id = ${userId}`);
}

// ASM-003: session fixation — session ID not regenerated after login
function login(req, res) {
  // Bug: reuses the pre-login session ID
  req.session.userId = req.body.userId;
  req.session.role = 'admin';
  res.json({ ok: true });
}

// ASM-004: JWT with algorithm:none allowed, no expiry on refresh token
const ACCESS_TOKEN_SECRET = 'weak-secret';
function issueTokens(userId) {
  const access = jwt.sign({ sub: userId }, ACCESS_TOKEN_SECRET, {
    algorithm: 'HS256',
    expiresIn: '30d',       // too long for access token
  });
  const refresh = jwt.sign({ sub: userId }, ACCESS_TOKEN_SECRET);  // no expiresIn
  return { access, refresh };
}

// ASM-005: account enumeration via distinct error messages
async function findUser(email) {
  const user = await db.findByEmail(email);
  if (!user) throw new Error('User not found');           // distinct message leaks existence
  if (!user.active) throw new Error('Account disabled'); // distinct message leaks status
  return user;
}

// ASM-006: password reset token is Math.random() — predictable
function generateResetToken() {
  return Math.random().toString(36).substring(2);
}

// ASM-007: no CSRF protection on state-changing endpoint
function updateEmail(req, res) {
  // Missing: validate CSRF token before processing
  db.query(`UPDATE users SET email = '${req.body.email}' WHERE id = ${req.session.userId}`);
  res.json({ ok: true });
}

// ASM-008: concurrent session not limited — unlimited parallel sessions allowed
function validateSession(token) {
  return jwt.verify(token, ACCESS_TOKEN_SECRET, { algorithms: ['HS256', 'none'] });
}

module.exports = { hashPassword, legacyHash, login, issueTokens, findUser, generateResetToken };
