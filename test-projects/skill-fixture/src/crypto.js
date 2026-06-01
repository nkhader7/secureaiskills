// audit-crypto-usage fixture
// Intentionally vulnerable — do not deploy

const crypto = require('crypto');
const https = require('https');

// ACU-001: MD5 for integrity check
function checksum(data) {
  return crypto.createHash('md5').update(data).digest('hex');
}

// ACU-001: SHA1 for signature
function sign(data) {
  return crypto.createHash('sha1').update(data).digest('hex');
}

// ACU-001: RC4 stream cipher (broken)
function encryptRC4(key, plaintext) {
  const cipher = crypto.createCipheriv('rc4', key, '');
  return cipher.update(plaintext, 'utf8', 'hex') + cipher.final('hex');
}

// ACU-001: DES-ECB (broken block cipher in ECB mode)
function encryptDES(key, plaintext) {
  const cipher = crypto.createCipheriv('des-ecb', key, '');
  cipher.setAutoPadding(true);
  return cipher.update(plaintext, 'utf8', 'base64') + cipher.final('base64');
}

// ACU-001: Triple-DES (deprecated)
function encrypt3DES(key, iv, plaintext) {
  const cipher = crypto.createCipheriv('des-ede3-cbc', key, iv);
  return cipher.update(plaintext, 'utf8', 'base64') + cipher.final('base64');
}

// ACU-002: TLS certificate verification disabled
const agent = new https.Agent({ rejectUnauthorized: false });
function fetchSecret(url) {
  return new Promise((resolve) => {
    https.get(url, { agent }, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve(data));
    });
  });
}

// ACU-003: hardcoded encryption key (static IV + static key)
const STATIC_KEY = Buffer.from('0123456789abcdef0123456789abcdef', 'hex');
const STATIC_IV  = Buffer.from('0000000000000000', 'hex');
function encryptAES_static(plaintext) {
  const cipher = crypto.createCipheriv('aes-128-cbc', STATIC_KEY, STATIC_IV);
  return cipher.update(plaintext, 'utf8', 'base64') + cipher.final('base64');
}

// ACU-004: weak RSA key size (512-bit)
function generateWeakRSA() {
  return crypto.generateKeyPairSync('rsa', { modulusLength: 512 });
}

// ACU-005: insecure random for security-sensitive purpose
function generateToken() {
  return Math.random().toString(36).substring(2, 15);  // not crypto-random
}

// ACU-006: AES in ECB mode — deterministic, patterns visible
function encryptAES_ECB(key, plaintext) {
  const cipher = crypto.createCipheriv('aes-128-ecb', key, '');
  return cipher.update(plaintext, 'utf8', 'base64') + cipher.final('base64');
}

module.exports = { checksum, sign, encryptRC4, encryptDES, encryptAES_static, generateToken };
