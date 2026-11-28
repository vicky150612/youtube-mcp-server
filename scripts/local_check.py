"""Build, test, and smoke-check the fixture MCP server."""
import subprocess
import sys


def main():
    steps = [
        ("Build", ["-m", "build"]),
        ("Automated tests", ["-m", "pytest", "-q"]),
        ("Launch fixture server and invoke get_video_details", ["scripts/smoke_mcp.py"]),
    ]
    results = []
    for name, args in steps:
        try:
            success = subprocess.run([sys.executable, *args], check=False, timeout=180).returncode == 0
        except subprocess.TimeoutExpired:
            success = False
        results.append(success)
        print(f"{'PASS' if success else 'FAIL'} {name}", flush=True)
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
