#!/usr/bin/env python3
"""
Prefix-aware HTTP server for testing.

Serves a static directory at both root and any path prefix detected in the
built site. Handles Eleventy pathPrefix so tests can run against builds with
BASE_URL set (e.g., GitHub Pages builds).

Usage:
    python scripts/test_server.py --directory _site --port 8080
"""

import os
import re
import sys
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler


def make_handler(prefix, directory):
    """Create a request handler class with the given prefix and directory.

    A factory function is needed because SimpleHTTPRequestHandler.__init__
    requires the directory to be passed as a keyword argument (Python 3.7+).
    """

    class _PrefixHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def translate_path(self, path):
            # Strip the path prefix if the request path starts with it
            if prefix and path.startswith(prefix + "/"):
                path = path[len(prefix):]
            elif prefix and path == prefix:
                path = "/"
            return super().translate_path(path)

    return _PrefixHandler


def detect_prefix(directory):
    """Auto-detect path prefix from built site index.html.

    Scans the generated HTML for href="/PREFIX/bengali/" patterns.
    Returns empty string if no prefix is found (normal local build).
    """
    index_path = os.path.join(directory, "index.html")
    if not os.path.exists(index_path):
        return ""

    with open(index_path, encoding="utf-8") as f:
        content = f.read(100000)

    # Look for href="/SOMETHING/bengali/" — the SOMETHING is the prefix
    m = re.search(r'href="(/[^"]+)/(?:bengali|hindi|english)/"', content)
    if m:
        return m.group(1)

    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Prefix-aware test HTTP server for VandanaGeetlyrics"
    )
    parser.add_argument(
        "--directory", default=".",
        help="Directory to serve (default: current directory)"
    )
    parser.add_argument(
        "--port", type=int, default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--prefix",
        help="Path prefix (auto-detected from index.html if omitted)"
    )
    args = parser.parse_args()

    directory = os.path.abspath(args.directory)

    if args.prefix is not None:
        prefix = args.prefix
    else:
        prefix = detect_prefix(directory)

    if prefix:
        print(f"  Path prefix detected: {prefix}")
    else:
        print("  No path prefix detected, serving at root")

    handler_class = make_handler(prefix, directory)
    server = HTTPServer(("", args.port), handler_class)
    print(f"  Serving {directory} on port {args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
