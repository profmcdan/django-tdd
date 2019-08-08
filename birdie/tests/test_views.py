from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.http import Http404
from django.core import mail
import pytest
from mixer.backend.django import mixer
from mock import patch
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
        req.user = AnonymousUser()
        obj = mixer.blend('birdie.Post')
        resp = views.PostUpdateView.as_view()(req, pk=obj.pk)
        assert resp.status_code == 200, "Should be callable by anyone"

    def test_post(self):
        post = mixer.blend('birdie.Post')
        data = {'body': 'New body text'}
        req = RequestFactory().post('/', data=data)
        req.user = AnonymousUser()
        resp = views.PostUpdateView.as_view()(req, pk=post.pk)
        assert resp.status_code == 302, "Should redirect to success view"
        post.refresh_from_db()
        assert post.body == "New body text", "Should update the post"

    def test_security(self):
        user = mixer.blend('auth.User', first_name='Martin')
        post = mixer.blend('birdie.Post')
        req = RequestFactory().post('/', data={})
        req.user = user
        with pytest.raises(Http404):
            views.PostUpdateView.as_view()(req, pk=post.pk)


class TestPaymentView:
    @patch('birdie.views.stripe')
    def test_payment(self, mock_stripe):
        mock_stripe.Charge.return_value = {'id': '234'}
        req = RequestFactory().post('/', data={'token': '123'})
        resp = views.PaymentView.as_view()(req)
        assert resp.status_code == 302, "Should redirect to success url"
        assert len(mail.outbox) == 1, "Should send an email"
