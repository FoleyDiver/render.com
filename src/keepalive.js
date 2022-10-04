const child_process = require('child_process');


module.exports.start = function () {
  // TODO gross and wrong
  if (process.env.ENV !== 'santa') return;

  // TODO configurate this URL
  const url = 'https://santa.onrender.com/keep-alive';

  const interval = setInterval(() => {
    const p = child_process.spawn('curl', ['-vs', url, '-m10'], {stdio: ['ignore', 'ignore', 'inherit']});
    p.unref();
    p.on('error', err => {
      console.error('child_process.spawn(curl) error:', err);
    });
  }, 5 * 60 * 1000);
  interval.unref();
};
