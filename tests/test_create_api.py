from datetime import datetime, timedelta
from app.models.url import URL


def test_create_without_expiration(auth_client, db):
    resp = auth_client.post("/api/create-short-url", json={
        "url": "https://example.com",
        "slug": "no-exp",
    })
    data = resp.get_json()
    assert data["success"] is True
    assert data.get("expires_at") is None
    assert data.get("is_expired") is False


def test_create_with_expiration(auth_client, db):
    future = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    resp = auth_client.post("/api/create-short-url", json={
        "url": "https://example.com",
        "slug": "with-exp",
        "expires_at": future,
    })
    data = resp.get_json()
    assert data["success"] is True
    assert data["expires_at"] is not None
    assert data["is_expired"] is False


def test_create_with_null_expiration(auth_client, db):
    resp = auth_client.post("/api/create-short-url", json={
        "url": "https://example.com",
        "slug": "null-exp",
        "expires_at": None,
    })
    data = resp.get_json()
    assert data["success"] is True
    assert data.get("expires_at") is None


def test_create_with_past_expiration_rejected(auth_client, db):
    past = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    resp = auth_client.post("/api/create-short-url", json={
        "url": "https://example.com",
        "slug": "past-exp",
        "expires_at": past,
    })
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_create_with_invalid_expiration_format(auth_client, db):
    resp = auth_client.post("/api/create-short-url", json={
        "url": "https://example.com",
        "slug": "bad-exp",
        "expires_at": "not-a-date",
    })
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False
