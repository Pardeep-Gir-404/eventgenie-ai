from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_headers_present():
    """Every response should carry baseline security headers."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "SAMEORIGIN"
    assert "referrer-policy" in response.headers


def test_cors_blocks_unknown_origin():
    """Unknown origins must not receive CORS allow headers."""
    response = client.get("/api/health", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_allows_local_dev_origin():
    """The local Vite dev origin stays allowed."""
    response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_path_traversal_is_not_served():
    """Encoded traversal attempts must never expose files outside the static dir."""
    response = client.get("/..%2f..%2f..%2fetc%2fpasswd")
    assert "root:" not in response.text