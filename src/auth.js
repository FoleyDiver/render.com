const crypto = require('crypto');
const util = require('util');

const pbkdf2 = util.promisify(crypto.pbkdf2);


function parseCookies (req) {
  const cookie = req.headers.cookie;
  if (!cookie) return {};

  return Object.fromEntries(cookie.split(';').map(s => s.trim()).map(cookieKvp => {
    const [name, ...valuePieces] = cookieKvp.split('=');
    return valuePieces.length > 0 ? [name, valuePieces.join('=')] : [];
  }));
}

function extractCookieToken (req) {
  return parseCookies(req).token;
}

function isTokenValid (token) {
  // TODO lolololol terrible. need timingsafeequals
  return token == createToken();
}

function createToken () {
  // TODO lolololol terrible strategy
  const [username, kdf, passwordPbkdf2, salt, iterations, dklen, hashalg] = process.env.CREDENTIALS.split(':');
  return passwordPbkdf2;
}


function extractBasicCredentials (req) {
  const auth = req.headers.authorization;
  if (!auth) return null;
  if (!auth.startsWith('Basic ')) return null;

  const [username, ...passwordPieces] = Buffer.from(auth.substr('Basic '.length), 'base64').toString('utf-8').split(':');
  if (passwordPieces.length === 0) return null;

  return {
    username,
    password: passwordPieces.join(':'),
  };
}

async function isAuthenticated (credentials) {
  const [username, kdf, passwordPbkdf2, salt, iterations, dklen, hashalg] = process.env.CREDENTIALS.split(':');
  if (kdf !== 'pbkdf2') {
    throw new Error(`Only 'pbkdf2' is supported, got '${kdf}'`);
  }

  if (credentials.username !== username) return false;

  const credsPasswordPbkdf2 = await pbkdf2(
    Buffer.from(credentials.password, 'utf-8'),
    Buffer.from(salt, 'hex'),
    parseInt(iterations, 10),
    parseInt(dklen, 10),
    hashalg,
  );
  return crypto.timingSafeEqual(credsPasswordPbkdf2, Buffer.from(passwordPbkdf2, 'hex'));
}


async function authenticate (req, res) {
  const token = extractCookieToken(req);
  if (token && isTokenValid(token)) {
    return true;
  }

  const credentials = extractBasicCredentials(req);
  if (credentials && await isAuthenticated(credentials)) {
    if (res) {
      res.setHeader('Set-Cookie', `token=${createToken()}; Expires=Wed, 31-Dec-2036 00:00:00 GMT; HttpOnly; Path=/`);
    }
    return true;
  }

  return false;
}


module.exports = {
  authenticate,
};
