// scan-exception-handling fixture
// Intentionally vulnerable — do not deploy

// EXC-001: fail-open — exception bypasses security check
function authorizeRequest(req) {
  try {
    return verifyJWT(req.headers.authorization);
  } catch (e) {
    return true;  // fail-open: grants access on any error
  }
}

// EXC-001: fail-open on authentication
function authenticate(token) {
  try {
    return jwt.verify(token, SECRET);
  } catch (err) {
    return { role: 'user' };  // returns a session object on failure
  }
}

// EXC-002: stack trace / internal detail returned to client
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,           // exposes internal stack trace
    query: err.sql,             // exposes raw SQL query
    config: process.env,        // exposes all environment variables
  });
});

// EXC-002: verbose DB error exposed
async function getUser(id) {
  try {
    return await db.query(`SELECT * FROM users WHERE id = ${id}`);
  } catch (err) {
    throw new Error(`Database error: ${err.message} (query: SELECT * FROM users WHERE id = ${id})`);
  }
}

// EXC-003: security exception swallowed silently
function validateInput(data) {
  try {
    schema.validate(data);
  } catch (validationError) {
    // swallowed — validation failure ignored, execution continues
  }
  return data;
}

// EXC-003: broad catch hides injection attempt
function runQuery(userInput) {
  try {
    return db.query(userInput);
  } catch (e) {
    // all errors silently ignored — attacker gets no feedback but injection still runs
  }
}

// EXC-004: finally block clears security state
function processPayment(req) {
  let authorized = false;
  try {
    authorized = authorize(req);
    return charge(req.body.amount);
  } finally {
    authorized = false;  // resets authorization flag unconditionally
  }
}

// EXC-005: sensitive data in custom exception message
class AuthError extends Error {
  constructor(user) {
    super(`Authentication failed for user ${user.email} with password hash ${user.passwordHash}`);
  }
}

module.exports = { authorizeRequest, authenticate, validateInput };
