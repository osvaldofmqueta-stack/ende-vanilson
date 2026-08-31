"""Find an available local TCP port for the Django development server."""

import socket
import sys


def find_free_port(start=8000, end=8999):
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    return None


if __name__ == "__main__":
    port = find_free_port()
    if port is None:
        print("Não foi encontrada nenhuma porta livre entre 8000 e 8999.", file=sys.stderr)
        raise SystemExit(1)
    print(port)