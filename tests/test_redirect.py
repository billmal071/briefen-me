from datetime import datetime, timedelta
from app.models.url import URL


def test_redirect_active_link(client, db):
    url = URL(original_url="https://example.com", slug="active")
    db.session.add(url)
    db.session.commit()
    resp = client.get("/active")
    assert resp.status_code == 302
    assert "example.com" in resp.headers["Location"]


def test_redirect_expired_shows_expired_page(client, db):
    url = URL(
        original_url="https://example.com",
        slug="old-link",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.session.add(url)
    db.session.commit()
    resp = client.get("/old-link")
    assert resp.status_code == 200
    assert b"expired" in resp.data.lower()
    assert b"https://example.com" in resp.data


def test_expired_link_no_click_tracking(client, db):
    url = URL(
        original_url="https://example.com",
        slug="expired-no-track",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.session.add(url)
    db.session.commit()
    client.get("/expired-no-track")
    refreshed = URL.query.filter_by(slug="expired-no-track").first()
    assert refreshed.click_count == 0


def test_redirect_no_expiration_works(client, db):
    url = URL(original_url="https://example.com/forever", slug="forever")
    db.session.add(url)
    db.session.commit()
    resp = client.get("/forever")
    assert resp.status_code == 302


def test_redirect_future_expiration_works(client, db):
    url = URL(
        original_url="https://example.com/future",
        slug="future",
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.session.add(url)
    db.session.commit()
    resp = client.get("/future")
    assert resp.status_code == 302
