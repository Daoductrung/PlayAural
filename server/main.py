"""Entry point for running the PlayAural v0.1 server with uv run main.py."""

import argparse
import asyncio
import sys
import os

# Ensure we can import from the package correctly
_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Change to script directory so relative paths work
os.chdir(_script_dir)

# Determine package name based on directory name (e.g. 'server' or 'pgame')
_pkg_name = os.path.basename(_script_dir)

try:
    from server.core.server import run_server
except ImportError:
    # Fallback for when directory is renamed (e.g. on VPS)
    import importlib
    try:
        _module = importlib.import_module(f"{_pkg_name}.core.server")
        run_server = _module.run_server
    except ImportError as e:
        print(f"CRITICAL: Could not import core server from 'server' or '{_pkg_name}'.")
        print(f"Ensure the parent directory ({_parent_dir}) is in PYTHONPATH.")
        print(f"Error detail: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PlayAural v0.1 Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default port (8000) without SSL
  uv run python main.py

  # Run on custom port
  uv run python main.py --port 9000

  # Run with SSL (WSS) using Let's Encrypt certificates
  uv run python main.py --ssl-cert /etc/letsencrypt/live/example.com/fullchain.pem \\
                        --ssl-key /etc/letsencrypt/live/example.com/privkey.pem

  # Run with SSL on custom port
  uv run python main.py --port 8443 --ssl-cert cert.pem --ssl-key key.pem
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
