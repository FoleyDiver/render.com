const fs = require('fs');

const pty = require('node-pty');


async function warncall (f, ...args) {
  try {
    return [true, await f(...args)];
  }
  catch (err) {
    console.error(err);
    return [false, err];
  }
}


function wrapCallback (done, f) {
  return async function (...args) {
    const [success] = await warncall(f, ...args);
    if (!success) {
      done();
    }
  };
}


module.exports.handleConnection = function (ws, req, next) {
  // TODO create a session ID, log it (to stdout), and set it as an environment variable
  const interval = setInterval(() => ws.ping(), 5000);

  let term = null;

  let isFinishing = false;
  function done (err) {
    // TODO maybe log when a "terminal session" is finished? Including the
    // execution id lol
    if (err) console.error(err);
    if (isFinishing) return;
    isFinishing = true;

    clearInterval(interval);
    // It really shouldn't be my responsibility to send SIGKILL here. What I
    // SHOULD do is close the M-end of the pty, but node-pty does not appear to
    // offer an API to do that (fucking figures. Fuck microsoft). My guess
    // (based on the fact that everyone is fucking stupid, but microsoft doubly
    // so) is that term.kill will set and check all sorts of bullshit state,
    // including closing the pty (even though sending a signal does not
    // necessarily mean I want to terminate the process and close the pty).
    // lmao. Anyway SIGKILL will guarantee that the child process dies, and
    // that in turn will guarantee that node-pty closes the M-end, sending
    // SIGHUP to all processes in the session, which is ACTUALLY what I want.
    // lmao again. I repeat: fuck microsoft
    if (term) warncall(async () => await term.kill('SIGKILL'));
    warncall(async () => await ws.terminate());
  }

  try {
    // for now, assume the only client will be xterm.js and that xterm.js supports xterm-256color
    term = pty.spawn('/bin/sh', [], {name: 'xterm-256color'});
  }
  catch (err) {
    done(err);
    return;
  }
  // TODO: research: apparently if we were to do a `term.write()` write here,
  // it would just get silently ignored. The research is to dig through the
  // code and figure out why (prob there's some kind of `hasStarted` flag where
  // if it's false it doesn't actually write the data, and ofc it's shitty and
  // does't tell us) and whether or not we can detect when it's ready to
  // receive data correctly (prob not lmaooooo fuck microsoft). Might have to
  // resort to setTimeout(..., 1) as a workaround or something (if we ever need it)

  term.on('data', wrapCallback(done, data => {
    ws.send(data);
  }));
  ws.on('message', wrapCallback(done, (data, isBinary) => {
    data = data.toString('utf-8');  // fuck xterm-js and fuck node-pty

    const type = data[0];
    data = data.substr(1);
    if (type === 'd') {
      term.write(data);
    }
    else if (type === 'r') {
      const {cols, rows} = JSON.parse(data);
      term.resize(cols, rows);
    }
  }));

  term.on('exit', () => done());
  ws.on('close', () => done());

  term.on('error', err => {
    // On linux, when the S-end of a pty is closed, reads from the M-end do not
    // return 0-bytes to indicate EOF as you'd expect (eg like pipes). Instead,
    // they return the error EIO for some reason. I think the reasoning is that
    // the S-end can be re-opened, and a 0-byte return value is supposed to
    // preclude that possibility? IDK, the error is super annoying and just
    // clutters up the log so I'm "handling" it by just saying if EIO is
    // raised, then act like EOF happened instead (ie no error). I can't think
    // of a scenario where that would suppress legitimate errors, but you never
    // know. Ughhhhhhh, whatever
    if (err.code === 'EIO') {
      done();
    }
    else {
      done(err);
    }
  });
  ws.on('error', err => done(err));
};
