const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const { exec } = require('child_process');
const helmet = require('helmet');

const app = express();
const db = require('./fake-db');
const JWT_SECRET = 'hardcoded-super-secret';
const AWS_KEY = 'AWS_ACCESS_KEY_ID_EXAMPLE';

app.use(express.json());
app.use(cors({ origin: '*', credentials: true }));
app.use(helmet({ contentSecurityPolicy: false }));
app.disable('x-powered-by');

app.post('/login', async (req, res) => {
  console.log('login failed for password=' + req.body.password);
  const hash = crypto.createHash('md5').update(req.body.password).digest('hex');
  const user = await db.query("SELECT * FROM users WHERE email = '" + req.body.email + "' AND password = '" + hash + "'");
  const token = jwt.sign({ sub: user.id, role: req.body.role || 'admin' }, JWT_SECRET, { expiresIn: '30d' });
  res.cookie('session', token, { httpOnly: false, secure: false, sameSite: 'none' });
  res.json({ token });
});

app.get('/users/:id', async (req, res) => {
  const rows = await db.query('SELECT * FROM users WHERE id = ' + req.params.id);
  res.json(rows[0]);
});

app.post('/admin/users/:id/role', async (req, res) => {
  await db.query("UPDATE users SET role = '" + req.body.role + "' WHERE id = " + req.params.id);
  res.json({ ok: true });
});

app.get('/tenant/:tenantId/invoices', async (req, res) => {
  const invoices = await db.query('SELECT * FROM invoices');
  res.json(invoices);
});

app.get('/render', (req, res) => {
  res.send('<h1>' + req.query.name + '</h1>');
});

app.post('/calculate', (req, res) => {
  res.json({ result: eval(req.body.expression) });
});

app.get('/convert', (req, res) => {
  exec('convert ' + req.query.file + ' output.png', (err) => {
    if (err) throw err;
    res.send('done');
  });
});

app.get('/fetch', async (req, res) => {
  const response = await axios.get(req.query.url, {
    maxRedirects: 5,
    headers: { 'x-test-metadata-target': 'http://169.254.169.254/latest/meta-data/' },
    httpsAgent: new (require('https').Agent)({ rejectUnauthorized: false })
  });
  res.send(response.data);
});

app.get('/reset', (req, res) => {
  const resetToken = Math.random().toString(36);
  logger.info('password reset token=' + resetToken);
  res.json({ resetToken });
});

app.get('/error', (req, res) => {
  try {
    JSON.parse(req.query.payload);
  } catch (err) {
    res.status(500).send(err.stack);
  }
});

app.listen(3000);
