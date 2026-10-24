"""Start the PlantIQ backend:  python run.py  [--host 0.0.0.0] [--port 8000] [--warm]"""
from __future__ import annotations

import argparse
import socket
import sys

import uvicorn


def lan_ips() -> list[str]:
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(ips)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--warm", action="store_true", help="load CNN + RAG at start-up instead of on first use")
    args = parser.parse_args()

    from app.core.config import settings

    print("\n  PlantIQ backend", settings.VERSION)
    print(f"  Local:   http://127.0.0.1:{args.port}")
    for ip in lan_ips():
        print(f"  Phone:   http://{ip}:{args.port}   ← enter this in the app's Server settings")
    print(f"  Docs:    http://127.0.0.1:{args.port}/docs\n")

    if args.warm:
        from app.services import registry

        registry.get_cnn()
        registry.get_rag()

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False, proxy_headers=settings.TRUST_PROXY_HEADERS,
                forwarded_allow_ips="*" if settings.TRUST_PROXY_HEADERS else None)


if __name__ == "__main__":
    main()
