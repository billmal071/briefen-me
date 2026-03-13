from datetime import datetime, timedelta
from app.models.url import URL


def _make_url(db, user, slug="test-edit", expires_at=None):
    url = URL(original_url="https://example.com", slug=slug, user_id=user.id, expires_at=expires_at)
    db.session.add(url)
    db.session.commit()
    return url


def test_edit_set_expiration(auth_client, db, user):
    url = _make_url(db, user)
    future = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    resp = auth_client.put(f"/api/edit-slug/{url.id}", json={
        "slug": url.slug,
        "expires_at": future,
    })
    data = resp.get_json()
    assert data["success"] is True
    assert data.get("expires_at") is not None
    refreshed = URL.query.get(url.id)
    assert refreshed.expires_at is not None


def test_edit_remove_expiration(auth_client, db, user):
    future = datetime.utcnow() + timedelta(days=7)
    url = _make_url(db, user, slug="has-exp", expires_at=future)
    resp = auth_client.put(f"/api/edit-slug/{url.id}", json={
        "slug": url.slug,
        "expires_at": None,
    })
    data = resp.get_json()
    assert data["success"] is True
    assert data.get("expires_at") is None
    refreshed = URL.query.get(url.id)
    assert refreshed.expires_at is None


def test_edit_slug_only_preserves_expiration(auth_client, db, user):
    future = datetime.utcnow() + timedelta(days=7)
    url = _make_url(db, user, slug="keep-exp", expires_at=future)
    resp = auth_client.put(f"/api/edit-slug/{url.id}", json={
        "slug": "new-slug-keep",
    })
    data = resp.get_json()
    assert data["success"] is True
    refreshed = URL.query.get(url.id)
    assert refreshed.expires_at is not None


def test_edit_past_expiration_rejected(auth_client, db, user):
    url = _make_url(db, user, slug="past-edit")
    past = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    resp = auth_client.put(f"/api/edit-slug/{url.id}", json={
        "slug": url.slug,
        "expires_at": past,
    })
    assert resp.status_code == 400
