// SAFE FIXTURE — scan-for-injection test
// Parameterized queries and validated inputs — should produce NO findings.

const db = require('./db');
const { execFile } = require('child_process');

// Safe: parameterized query
function getUserById(req, res) {
  db.query('SELECT * FROM users WHERE id = $1', [parseInt(req.params.id, 10)],
    (err, rows) => res.json(rows));
}

// Safe: prepared statement
function searchUsers(req, res) {
  const stmt = db.prepare('SELECT * FROM users WHERE name = ?');
  stmt.all([req.query.name], (err, rows) => res.json(rows));
}

// Safe: execFile with array args (no shell expansion)
function convertFile(req, res) {
  const allowed = /^[a-z0-9_-]+\.png$/i;
  if (!allowed.test(req.query.file)) return res.status(400).end();
  execFile('convert', [req.query.file, 'output.png'], (err) => res.send('done'));
}

// Safe: constant expression, not user-controlled
function getVersion() {
  return eval('"1.0.0"');
}
