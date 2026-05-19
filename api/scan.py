import json
import asyncio
from io import BytesIO

from wsgiref.util import setup_testing_defaults

from backend.api.main import ScanRequest, run_scan


def app(environ, start_response):
    """WSGI entrypoint for Vercel Python serverless function.

    Expects a JSON POST with the same shape as the existing API `/api/scan`.
    This wrapper calls the existing `run_scan` coroutine and returns its
    serialized JSON response. It keeps all scanning logic unchanged.
    """
    setup_testing_defaults(environ)

    method = environ.get("REQUEST_METHOD", "GET").upper()
    if method == "OPTIONS":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"OK"]

    if method != "POST":
        start_response("405 Method Not Allowed", [("Content-Type", "text/plain")])
        return [b"Method Not Allowed"]

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0

    body = environ["wsgi.input"].read(length) if length else b""
    try:
        payload = json.loads(body.decode("utf-8")) if body else {}
    except Exception:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [json.dumps({"error": "Invalid JSON"}).encode()]

    # Build the ScanRequest pydantic model from payload
    try:
        req = ScanRequest(**payload)
    except Exception as e:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [json.dumps({"error": "Invalid request payload", "detail": str(e)}).encode()]

    try:
        result = asyncio.run(run_scan(req))
        body_out = json.dumps(result.dict(), default=str)
        start_response("200 OK", [("Content-Type", "application/json")])
        return [body_out.encode("utf-8")]
    except Exception as e:
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps({"error": "scan_failed", "detail": str(e)}).encode()]
