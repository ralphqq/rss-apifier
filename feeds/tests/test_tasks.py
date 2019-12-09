import random
from unittest.mock import patch

from django.test import TestCase

from feeds.models import Feed
from feeds.tasks import fetch_entries
from feeds.tests.helpers import create_and_save_feeds


@patch('feeds.tasks.Feed.update_feed_entries')
class FetchEntriesTest(TestCase):

    def setUp(self):
        self.feeds = create_and_save_feeds(5)
        self.saved_entry_counts = [
            random.randint(5, 20) for i in range(self.feeds.count())
        ]

    def tearDown(self):
        Feed.objects.all().delete()

    def test_successful_fetch_process(self, mock_update):
        mock_update.side_effect = self.saved_entry_counts
        res = fetch_entries()
        self.assertEqual(res, sum(self.saved_entry_counts))
        self.assertEqual(mock_update.call_count, self.feeds.count())

    def test_when_no_feeds_are_found(self, mock_update):
        self.feeds.delete()
        res = fetch_entries()
        self.assertIsNone(res)
        self.assertFalse(mock_update.called)

    def test_errors_during_processing(self, mock_update):
        self.saved_entry_counts[1] = Exception
        mock_update.side_effect = self.saved_entry_counts
        res = fetch_entries()
        self.assertEqual(
            res,
            sum(filter(lambda x: x != Exception, self.saved_entry_counts))
        )
        self.assertEqual(mock_update.call_count, self.feeds.count())
