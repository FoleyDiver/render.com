#!/usr/bin/env python3

import os  # noqa:F401
import sys  # noqa:F401
import json
import subprocess

from proc import iter_procs, display


def main (arg0, argv):
    procs = sorted(iter_procs(), key=lambda proc: proc.statm.private, reverse=True)
    with subprocess.Popen(["/app/bin/json2table", "-w+", "-a", "cmd=-"], stdin=subprocess.PIPE, text=True) as p:
        for proc in procs:
            if proc.cmd:
                print(json.dumps(display(proc)), file=p.stdin)

if __name__ == "__main__":
    try:
        c = main(sys.argv[0], sys.argv[1:])
    except (KeyboardInterrupt, BrokenPipeError):
        sys.stderr.close()
        raise
    if c:
        sys.exit(c)
