from datetime import datetime, timedelta
from app.models.url import URL


def test_url_default_no_expiration(app, db):
    url = URL(original_url="https://example.com", slug="test-1")
    db.session.add(url)
    db.session.commit()
    assert url.expires_at is None
    assert url.is_expired is False


def test_url_not_expired(app, db):
    url = URL(
        original_url="https://example.com",
        slug="test-2",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.session.add(url)
    db.session.commit()
    assert url.is_expired is False


def test_url_is_expired(app, db):
    url = URL(
        original_url="https://example.com",
        slug="test-3",
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.session.add(url)
    db.session.commit()
    assert url.is_expired is True


def test_url_expires_at_persisted(app, db):
    future = datetime.utcnow() + timedelta(days=30)
    url = URL(original_url="https://example.com", slug="test-4", expires_at=future)
    db.session.add(url)
    db.session.commit()
    fetched = URL.query.filter_by(slug="test-4").first()
    assert fetched.expires_at is not None
    assert abs((fetched.expires_at - future).total_seconds()) < 1
