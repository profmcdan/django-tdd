import pytest
from django.contrib.admin.sites import AdminSite
from mixer.backend.django import mixer
from .. import admin, models, forms

pytestmark = pytest.mark.django_db


class TestPostForm:
    def test_form(self):
        form = forms.PostForm(data={})
        assert form.is_valid() is False, "Should be invalid if no data is given"

        form = forms.PostForm(data={"body": "Hello"})
        assert form.is_valid() is False, "Should be invalid if too short"
        assert 'body' in form.errors, "Should have body field error"

        form = forms.PostForm(data={"body": "Hello World !!!!!!!!!!!!!!!"})
        assert form.is_valid() is True, "Should be valid if long enough"
