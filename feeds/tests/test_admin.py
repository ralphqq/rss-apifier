from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from feeds.admin import FeedAdmin
from feeds.models import Feed


@patch('feeds.admin.Feed.save')
class FeedAdminTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.feed_admin = FeedAdmin(Feed, self.site)

    
    def test_save_model(self, mock_save):
        self.feed_admin.save_model(
            request=None,
            obj=Feed,
            form=None,
            change=None
        )
        self.assertTrue(mock_save.called)

    def test_save_model_handles_errors(self, mock_save):
        mock_save.return_value = Exception

        # This should not raise an exception:
        self.feed_admin.save_model(
            request=None,
            obj=Feed,
            form=None,
            change=None
        )
