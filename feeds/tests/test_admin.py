from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from feeds.admin import FeedAdmin
from feeds.models import Feed


class FeedAdminTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.feed_admin = FeedAdmin(model=Feed, admin_site=self.site)

        # Create and log a super user in
        username = 'admin'
        password = '123456'
        self.admin_user = User.objects.create_superuser(
            username=username,
            email=None,
            password=password
        )
        self.client.login(username=username, password=password)

        # Create a fake request object
        request_factory = RequestFactory()
        self.request = request_factory.get('/admin')
        self.request.user = self.admin_user

    @patch('feeds.admin.Feed.save')
    def test_save_model(self, mock_save):
        self.feed_admin.save_model(
            request=None,
            obj=Feed,
            form=None,
            change=None
        )
        self.assertTrue(mock_save.called)

    @patch('feeds.admin.Feed.save')
    def test_save_model_raises_saving_errors(self, mock_save):
        mock_save.side_effect = Exception
        with self.assertRaises(Exception):
            self.feed_admin.save_model(
            request=None,
            obj=Feed,
            form=None,
            change=None
        )

    @patch('feeds.admin.FeedAdmin.message_user')
    @patch('feeds.admin.admin.ModelAdmin.changeform_view')
    def test_admin_feed_obj_creation_errors(
            self,
            mock_super_changeform_view,
            mock_message
        ):
        mock_super_changeform_view.side_effect = ValueError('Some error')

        # This should not raise an exception
        # because exceptions are caught by the overridden method
        response = self.feed_admin.changeform_view(request=self.request)

        # Super method gets called
        self.assertTrue(mock_super_changeform_view.called)

        # Page shows error message and redirects user
        self.assertTrue(mock_message.called)
        self.assertEqual(response.status_code, 302)
