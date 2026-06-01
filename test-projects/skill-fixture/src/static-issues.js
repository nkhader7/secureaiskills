// scan-static-analysis fixture
// Intentionally vulnerable — do not deploy

// SAS: hardcoded IP addresses
const DB_HOST = '192.168.1.50';
const INTERNAL_API = 'http://10.0.0.5:8080/internal';
const BACKUP_SERVER = '172.16.0.100';

// SAS: magic numbers with no explanation
function calculateTimeout(retries) {
  return retries * 3000 + 42000;   // 42000 = magic number
}

function getMaxUpload() {
  return 52428800;   // 50MB as magic number — should be a named constant
}

// SAS: TODO/FIXME security notes left in production code
// TODO: add authentication before deploying
// FIXME: this allows SQL injection, fix before go-live
// HACK: bypassing auth check for demo
// SECURITY: need to sanitize this input

// SAS: console.log left in production path
function processPayment(card) {
  console.log('Processing card:', card.number, card.cvv);
  console.log('Card holder:', card.name);
  return chargeCard(card);
}

// SAS: eval() with dynamic input
function calculate(expression) {
  return eval(expression);   // arbitrary code execution
}

// SAS: Function() constructor (equivalent to eval)
function buildValidator(rules) {
  const fn = new Function('data', rules);
  return fn;
}

// SAS: disabled lint/security rules
/* eslint-disable no-eval */
/* eslint-disable security/detect-eval-with-expression */
/* eslint-disable security/detect-non-literal-regexp */

// SAS: dead code / unreachable branch
function getRole(user) {
  return 'admin';           // always returns admin
  if (user.role) {          // unreachable
    return user.role;
  }
}

// SAS: unused security variable
const ENABLE_AUTH = true;
// ENABLE_AUTH is never checked anywhere

// SAS: non-literal RegExp from user input (ReDoS risk)
function search(pattern, text) {
  const re = new RegExp(pattern);   // user-controlled regex
  return re.test(text);
}

// SAS: prototype pollution vector
function merge(target, source) {
  for (const key of Object.keys(source)) {
    target[key] = source[key];   // __proto__ not blocked
  }
  return target;
}

// SAS: path traversal via string concatenation
const BASE_DIR = '/app/uploads/';
function readFile(filename) {
  return fs.readFileSync(BASE_DIR + filename);   // no path normalization
}

module.exports = { calculate, search, merge, readFile };
