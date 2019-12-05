from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from feeds.forms import FeedAdminAddForm, FeedAdminChangeForm


@patch('feeds.models.Feed.fetch_and_set_feed_details')
class FeedAdminAddFormTest(TestCase):

    def test_invalid_when_link_is_missing(self, mock_fetch):
        form = FeedAdminAddForm(data={})
        self.assertFalse(form.is_valid())

    def test_valid_link(self, mock_fetch):
        data = {'link': 'https://some-feed.com/'}
        form = FeedAdminAddForm(data=data)
        self.assertTrue(form.is_valid())

    def test_saving_new_feed_calls_fetch(self, mock_fetch):
        data = {'link': 'https://some-feed.com/'}
        form = FeedAdminAddForm(data=data)
        form.save()
        self.assertTrue(mock_fetch.called)


@patch('feeds.models.Feed.fetch_and_set_feed_details')
class FeedAdminChangeFormTest(TestCase):

    def test_invalid_when_link_is_missing(self, mock_fetch):
        form = FeedAdminChangeForm(data={})
        self.assertFalse(form.is_valid())

    def test_ok_even_if_missing_title_and_description(self, mock_fetch):
        data = {'link': 'https://some-feed.com/'}
        form = FeedAdminChangeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_updating_existing_feed(self, mock_fetch):
        with patch('feeds.models.Feed.objects.get') as mock_get:
            mock_get.return_value = True
            data = {
                'link': 'https://some-feed.com/',
                'title': 'Title',
                'description': 'Description'
            }
            form = FeedAdminAddForm(data=data)
            form.save()

        self.assertFalse(mock_fetch.called)
