"""
Serve the benchmark web app.
Runs benchmark.py if results/benchmark-results.json is missing or stale,
then starts a local HTTP server on port 8080.
"""

import http.server
import subprocess
import sys
import webbrowser
from pathlib import Path

BENCH_DIR = Path(__file__).parent
RESULTS_FILE = BENCH_DIR / "results" / "benchmark-results.json"
APP_DIR = BENCH_DIR / "app"
PORT = 8080


def maybe_run_benchmark():
    if not RESULTS_FILE.exists():
        print("benchmark-results.json not found — running benchmark.py …")
        subprocess.run([sys.executable, str(BENCH_DIR / "benchmark.py")], check=True)
    else:
        print(f"Using existing results: {RESULTS_FILE}")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BENCH_DIR), **kwargs)

    def do_GET(self):
        # Rewrite / to the full skills test lab. The benchmark dashboard remains
        # available at /app/index.html.
        if self.path in ("", "/"):
            self.path = "/app/index.html"
        super().do_GET()

    def log_message(self, fmt, *args):
        # suppress normal access log noise
        if "benchmark-results" in args[0] if args else False:
            return
        super().log_message(fmt, *args)


def main():
    maybe_run_benchmark()

    url = f"http://localhost:{PORT}"
    print(f"\nServing at {url}")
    print("Press Ctrl+C to stop.\n")
    webbrowser.open(url)

    with http.server.HTTPServer(("", PORT), Handler) as srv:
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
