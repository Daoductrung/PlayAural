"""Entry point for running the PlayAural v0.1 server."""

import argparse
import asyncio

from .core.server import run_server


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PlayAural v0.1 Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default port (8000) without SSL
  python -m server

  # Run on custom port
  python -m server --port 9000

  # Run with SSL (WSS) using Let's Encrypt certificates
  python -m server --ssl-cert /etc/letsencrypt/live/example.com/fullchain.pem \\
                   --ssl-key /etc/letsencrypt/live/example.com/privkey.pem

  # Run with SSL on custom port
  python -m server --port 8443 --ssl-cert cert.pem --ssl-key key.pem
""",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to listen on (default: 8000)",
    )
    parser.add_argument(
        "--ssl-cert",
        dest="ssl_cert",
        help="Path to SSL certificate file (enables WSS). For Let's Encrypt, use fullchain.pem",
    )
    parser.add_argument(
        "--ssl-key",
        dest="ssl_key",
        help="Path to SSL private key file. For Let's Encrypt, use privkey.pem",
    )

    args = parser.parse_args()

    # Validate SSL arguments
    if (args.ssl_cert and not args.ssl_key) or (args.ssl_key and not args.ssl_cert):
        parser.error("Both --ssl-cert and --ssl-key must be provided together")

    protocol = "wss" if args.ssl_cert else "ws"
    print(f"Starting PlayAural v0.1 server on {protocol}://{args.host}:{args.port}")

    asyncio.run(
        run_server(
            host=args.host,
            port=args.port,
            ssl_cert=args.ssl_cert,
            ssl_key=args.ssl_key,
        )
    )


if __name__ == "__main__":
    main()
