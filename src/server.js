const process = require('process');
const http = require('http');

const express = require('express');
const morgan = require('morgan');
const { WebSocketServer } = require('ws');

const auth = require('./auth.js');
const term = require('./term.js');
const lawg = require('./lawg.js');


module.exports.start = function () {
  const app = express();
  const server = http.createServer(app);
  const wss = new WebSocketServer({
    server,
    clientTracking: false,
    maxPayload: 1 * 1024 * 1024,
    verifyClient ({req}, callback) {
      auth.authenticate(req).then(isAuthed => {
        callback(isAuthed, 401, '401 Unauthorized\n', {'WWW-Authenticate': 'Basic'});
      });
    },
  });
  const lawgger = lawg.Lawgger();

  app.set('x-powered-by', false);
  app.use(morgan('combined'));
  app.use(async (req, res, next) => {
    if (await auth.authenticate(req, res)) {
      next();
    }
    else {
      res.status(401);
      res.setHeader('WWW-Authenticate', 'Basic');
      res.send('401 Unauthorized\n');
    }
  });
  app.use(express.static('./public'));
  app.use(express.raw({type: () => true}));

  wss.on('connection', term.handleConnection);
  app.post('/lawg', async (req, res) => {
    await lawgger.lawg(req.body);
    res.send('');
  });
  app.post('/close', (req, res) => {
    res.send('ok\n');
    server.close();
  });

  server.listen(parseInt(process.env.PORT, 10), '0.0.0.0', () => {
    const {address, port} = server.address();
    console.log(`Listening on ${address}:${port}`);
  });
};
