from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
import pytest
from mixer.backend.django import mixer
from .. import views

pytestmark = pytest.mark.django_db


class TestHomeView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        resp = views.HomeView.as_view()(req)
        assert resp.status_code == 200, "Should be callable  by anyone"


class TestAdminView:
    def test_anonymous(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        resp = views.AdminView.as_view()(req)
        assert "login" in resp.url, "should redirect to login"

    def test_superuser_authenticated(self):
        user = mixer.blend('auth.User', is_superuser=True)
        req = RequestFactory().get('/')
        req.user = user
        resp = views.AdminView.as_view()(req)
        assert resp.status_code == 200, "Should allow authenticate user to access"


class TestPostUpdateView:
    def test_get(self):
        req = RequestFactory().get('/')
        obj = mixer.blend('birdie.Post')
        resp = views.PostUpdateView.as_view()(req, pk=obj.pk)
        assert resp.status_code == 200, "Should be callable by anyone"

    def test_post(self):
        post = mixer.blend('birdie.Post')
        data = {'body': 'New body text'}
        req = RequestFactory().post('/', data=data)
        resp = views.PostUpdateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 302, "Should redirect to success view"
        post.refresh_from_db()
        assert post.body == "New body text", "Should update the post"
