// EDGE CASE FIXTURE — scan-for-injection
// Cases where detection is correct but context matters.

// Edge: SQL keyword inside a variable name (should still match — rule is evidence-based)
const deleteFrom = (table) => `SELECT * FROM ${table} WHERE active = 1`;

// Edge: eval of a static string (no user input — low risk, but pattern matches)
const version = eval('"2.1.0"');

// Edge: template literal with only numeric user input
function getPage(req) {
  const page = parseInt(req.query.page, 10) || 1;
  return `SELECT * FROM posts LIMIT 10 OFFSET ${page * 10}`;
}

// Edge: exec used with a whitelisted constant (pattern will match command)
const exec = require('child_process').exec;
exec('git status');
