from datetime import datetime, timedelta
from app.models.url import URL


def test_analytics_includes_expiration_fields(auth_client, db, user):
    future = datetime.utcnow() + timedelta(days=7)
    url = URL(original_url="https://example.com", slug="analytics-exp", user_id=user.id, expires_at=future)
    db.session.add(url)
    db.session.commit()
    resp = auth_client.get("/api/analytics/analytics-exp")
    data = resp.get_json()
    assert data["success"] is True
    assert "expires_at" in data
    assert "is_expired" in data
    assert data["is_expired"] is False


def test_analytics_no_expiration(auth_client, db, user):
    url = URL(original_url="https://example.com", slug="analytics-no-exp", user_id=user.id)
    db.session.add(url)
    db.session.commit()
    resp = auth_client.get("/api/analytics/analytics-no-exp")
    data = resp.get_json()
    assert data["expires_at"] is None
    assert data["is_expired"] is False


def test_analytics_expired_link(auth_client, db, user):
    past = datetime.utcnow() - timedelta(hours=1)
    url = URL(original_url="https://example.com", slug="analytics-dead", user_id=user.id, expires_at=past)
    db.session.add(url)
    db.session.commit()
    resp = auth_client.get("/api/analytics/analytics-dead")
    data = resp.get_json()
    assert data["is_expired"] is True
