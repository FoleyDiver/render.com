#!/usr/bin/env python3

import os
import sys
import socket

def main (arg0, argv):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", 8445))
        host, port, *_ = sock.getsockname()
        print(f"Listening on {host}:{port} ...")
        while True:
            msg, (host, port) = sock.recvfrom(2**16-1)
            print(f"{msg!a}"[2:-1])

if __name__ == "__main__":
    try:
        c = main(sys.argv[0], sys.argv[1:])
    except (KeyboardInterrupt, BrokenPipeError):
        sys.stderr.close()
        raise
    if c:
        sys.exit(c)
