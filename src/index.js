const process = require('process');

const server = require('./server.js');
const keepalive = require('./keepalive.js');


server.start();
keepalive.start();

process.once('SIGTERM', sig => {
  // I don't THINK I need to bother going through and killing all subprocesses
  // spawned by `./term.js`. The M-ends of their PTYs will all close, causing
  // SIGHUP to get sent to all processes in the session, which by default kills
  // them (I'm not gonna worry about misbehaving processes), and then they get
  // reaped by pid 1 (tini)
  console.log(`Signal: ${sig}`);
  process.kill(process.pid, sig);
});
