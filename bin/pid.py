#!/usr/bin/env python3

import os  # noqa:F401
import sys  # noqa:F401
import json
import subprocess

from proc import iter_procs, display


def main (arg0, argv):
    procs_by_pid = {int(pid): [] for pid in (argv or [1])}

    for proc in iter_procs():
        if (procs := procs_by_pid.get(proc.pid)) is not None:
            procs.insert(0, proc)
        elif (procs := procs_by_pid.get(proc.stat.ppid)) is not None:
            procs.append(proc)


    with subprocess.Popen(["/app/bin/json2table", "-w+", "-a", "cmd=-"], stdin=subprocess.PIPE, text=True) as p:
        for procs in procs_by_pid.values():
            for proc in procs:
                print(json.dumps(display(proc)), file=p.stdin)

if __name__ == "__main__":
    try:
        c = main(sys.argv[0], sys.argv[1:])
    except (KeyboardInterrupt, BrokenPipeError):
        sys.stderr.close()
        raise
    if c:
        sys.exit(c)
