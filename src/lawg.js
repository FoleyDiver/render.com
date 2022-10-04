const dgram = require('dgram');
const util = require('util');


module.exports.Lawgger = function () {
  const sock = dgram.createSocket('udp4');
  const sendto = util.promisify(sock.send.bind(sock));

  async function lawg (msg) {
    try {
      await sendto(msg, 8445, '127.0.0.1');
    }
    catch (err) {
      console.error('sendto:', err);
    }
  }

  return {
    lawg,
  };
};
