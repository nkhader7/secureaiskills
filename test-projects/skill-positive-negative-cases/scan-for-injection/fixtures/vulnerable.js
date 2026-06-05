// VULNERABLE FIXTURE — scan-for-injection test
// All patterns here are intentionally insecure for testing purposes only.

const db = require('./db');
const { exec, execFile } = require('child_process');

// SI-001: SQL injection via template literal (critical)
function getUserById(req, res) {
  const query = `SELECT * FROM users WHERE id = '${req.params.id}'`;
  db.query(query, (err, rows) => res.json(rows));
}

// SI-001: SQL injection via string concatenation
function searchUsers(req, res) {
  const q = "SELECT * FROM users WHERE name = '" + req.query.name + "'";
  db.query(q);
}

// SI-002: Command injection via exec
function convertFile(req, res) {
  exec('convert ' + req.query.file + ' output.png', (err) => res.send('done'));
}

// SI-002: Command injection via shell_exec equivalent
function runReport(req, res) {
  const cmd = `ls -la /reports/${req.body.folder}`;
  exec(cmd);
}

// SI-003: Code injection via eval with user input
function calculate(req, res) {
  const result = eval(req.body.expression);
  res.json({ result });
}

// SI-004: NoSQL injection
function findUser(req, res) {
  db.users.findOne({ $where: req.body.filter });
}
