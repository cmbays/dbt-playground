#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""
Browser testing CLI for playground validation.

Loads HTML files in headless Chromium via Playwright and captures console
messages, network failures, and optional screenshots. Outputs structured JSON.

Usage:
    uv run scripts/browser-test.py <html-file> [options]

Examples:
    # Basic test - check for console errors
    uv run scripts/browser-test.py playgrounds/mermaid-designer.html

    # With screenshot
    uv run scripts/browser-test.py playgrounds/workflow-hub.html \
        --screenshot temp/hub-screenshot.png

    # Fail on any console errors (for CI)
    uv run scripts/browser-test.py playgrounds/workflow-hub.html \
        --check-no-errors

    # Custom timeout for slow pages
    uv run scripts/browser-test.py playgrounds/mermaid-designer.html \
        --timeout 10000
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def check_server_running(port: int) -> bool:
    """Check if the playground server is running on the specified port."""
    try:
        url = f"http://localhost:{port}/api/health"
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())
            return data.get("status") == "ok"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return False


def resolve_html_path(file_path: str, project_root: Path) -> tuple[str, str] | None:
    """
    Resolve the HTML file path to a URL path.

    Returns tuple of (url_path, resolved_file_path) or None if file not found.
    """
    path = Path(file_path)

    # If absolute path, use it directly
    if path.is_absolute():
        resolved = path
    else:
        # Try relative to project root
        resolved = project_root / path
        if not resolved.exists():
            # Try relative to current directory
            resolved = Path.cwd() / path

    if not resolved.exists():
        return None

    # Convert to URL path relative to project root
    try:
        relative = resolved.resolve().relative_to(project_root.resolve())
        url_path = "/" + str(relative).replace("\\", "/")
        return url_path, str(resolved)
    except ValueError:
        # File is outside project root - can't serve it
        return None


def run_browser_test(
    file_path: str,
    port: int = 5050,
    timeout_ms: int = 5000,
    screenshot_path: str | None = None,
    check_no_errors: bool = False,
) -> dict:
    """
    Run browser test on an HTML file and return results.

    Args:
        file_path: Path to the HTML file to test
        port: Server port (default 5050)
        timeout_ms: Page load timeout in milliseconds
        screenshot_path: Optional path to save screenshot
        check_no_errors: If True, set success=False on any console errors

    Returns:
        Dict with test results including console messages and network failures
    """
    start_time = time.time()

    # Initialize result structure
    result = {
        "success": True,
        "url": "",
        "console": {
            "errors": [],
            "warnings": [],
            "logs": [],
        },
        "network": {
            "failed": [],
        },
        "screenshot": None,
        "duration_ms": 0,
    }

    # Determine project root (script is in scripts/ directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Resolve file path to URL
    path_result = resolve_html_path(file_path, project_root)
    if path_result is None:
        result["success"] = False
        result["console"]["errors"].append({
            "type": "error",
            "text": f"File not found: {file_path}",
            "location": "browser-test.py",
        })
        result["duration_ms"] = int((time.time() - start_time) * 1000)
        return result

    url_path, resolved_path = path_result
    url = f"http://localhost:{port}{url_path}"
    result["url"] = url

    # Check if server is running
    if not check_server_running(port):
        result["success"] = False
        result["console"]["errors"].append({
            "type": "error",
            "text": f"Server not running on port {port}. Start it with: uv run scripts/playground-server.py",
            "location": "browser-test.py",
        })
        result["duration_ms"] = int((time.time() - start_time) * 1000)
        return result

    # Import Playwright (may not be installed)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result["success"] = False
        result["console"]["errors"].append({
            "type": "error",
            "text": "Playwright not installed. Run: uv add playwright && uv run playwright install chromium",
            "location": "browser-test.py",
        })
        result["duration_ms"] = int((time.time() - start_time) * 1000)
        return result

    # Run browser test
    try:
        with sync_playwright() as p:
            # Launch headless Chromium
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                result["success"] = False
                error_text = str(e)
                if "Executable doesn't exist" in error_text:
                    error_text = "Chromium not installed. Run: uv run playwright install chromium"
                result["console"]["errors"].append({
                    "type": "error",
                    "text": error_text,
                    "location": "browser-test.py",
                })
                result["duration_ms"] = int((time.time() - start_time) * 1000)
                return result

            page = browser.new_page()

            # Set up console message handler
            def handle_console(msg):
                msg_type = msg.type
                location = msg.location
                location_str = ""
                if location:
                    location_str = f"{location.get('url', '')}:{location.get('lineNumber', '')}:{location.get('columnNumber', '')}"

                entry = {
                    "type": msg_type,
                    "text": msg.text,
                    "location": location_str,
                }

                if msg_type == "error":
                    result["console"]["errors"].append(entry)
                elif msg_type == "warning":
                    result["console"]["warnings"].append(entry)
                else:
                    result["console"]["logs"].append(entry)

            page.on("console", handle_console)

            # Set up network failure handler
            def handle_request_failed(request):
                result["network"]["failed"].append({
                    "url": request.url,
                    "status": 0,
                    "error": request.failure or "Request failed",
                })

            page.on("requestfailed", handle_request_failed)

            # Also capture HTTP errors (4xx, 5xx)
            def handle_response(response):
                if response.status >= 400:
                    result["network"]["failed"].append({
                        "url": response.url,
                        "status": response.status,
                        "error": response.status_text,
                    })

            page.on("response", handle_response)

            # Navigate to page
            try:
                page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            except Exception as e:
                # Page might have loaded but timed out waiting for network idle
                # This is often OK for pages with long-polling or websockets
                if "Timeout" in str(e):
                    result["console"]["warnings"].append({
                        "type": "warning",
                        "text": f"Page load timed out after {timeout_ms}ms (network not idle)",
                        "location": "browser-test.py",
                    })
                else:
                    result["success"] = False
                    result["console"]["errors"].append({
                        "type": "error",
                        "text": f"Navigation failed: {e}",
                        "location": "browser-test.py",
                    })
                    result["duration_ms"] = int((time.time() - start_time) * 1000)
                    browser.close()
                    return result

            # Give a moment for any deferred JS to execute
            page.wait_for_timeout(500)

            # Take screenshot if requested
            if screenshot_path:
                screenshot_full_path = Path(screenshot_path)
                if not screenshot_full_path.is_absolute():
                    screenshot_full_path = project_root / screenshot_path
                screenshot_full_path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshot_full_path), full_page=True)
                result["screenshot"] = str(screenshot_full_path)

            browser.close()

    except Exception as e:
        result["success"] = False
        result["console"]["errors"].append({
            "type": "error",
            "text": f"Browser test failed: {e}",
            "location": "browser-test.py",
        })

    # Check for errors if requested
    if check_no_errors and result["console"]["errors"]:
        result["success"] = False

    result["duration_ms"] = int((time.time() - start_time) * 1000)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Browser test for HTML playgrounds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s playgrounds/workflow-hub.html
  %(prog)s playgrounds/mermaid-designer.html --screenshot temp/screenshot.png
  %(prog)s playgrounds/workflow-hub.html --check-no-errors --timeout 10000
        """,
    )
    parser.add_argument(
        "file",
        help="HTML file to test (relative to project root or absolute path)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5050,
        help="Server port (default: 5050)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5000,
        metavar="MS",
        help="Page load timeout in milliseconds (default: 5000)",
    )
    parser.add_argument(
        "--screenshot",
        metavar="PATH",
        help="Save screenshot to specified path",
    )
    parser.add_argument(
        "--check-no-errors",
        action="store_true",
        help="Exit with code 1 if any console errors are captured",
    )

    args = parser.parse_args()

    # Run the test
    result = run_browser_test(
        file_path=args.file,
        port=args.port,
        timeout_ms=args.timeout,
        screenshot_path=args.screenshot,
        check_no_errors=args.check_no_errors,
    )

    # Output JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
