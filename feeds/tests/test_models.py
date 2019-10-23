from unittest.mock import patch

from django.db.utils import IntegrityError
from django.test import TestCase

from feeds.tests.helpers import make_fake_feedparser_dict
from feeds.models import Feed


class FeedModelTest(TestCase):

    def setUp(self):
        self.feed_url = 'https://www.samplefeeds.com/rss'   # fake URL

        # Create and set a valid FeedParserDict object
        # to be used or overridden in the tests
        self.feedparser_dict = make_fake_feedparser_dict(self.feed_url)

        # Patch the fetch_feedparser_dict utility function
        patcher = patch(
            'feeds.models.fetch_feedparser_dict',
            return_value=self.feedparser_dict
        )
        self.mock_fetch_feedparser_dict = patcher.start()

        # To ensure patch gets cleaned up during tearDown:
        self.addCleanup(patcher.stop)

    def test_feed_save_method(self):
        feed = Feed(link=self.feed_url)
        feed.save()
        new_feed = Feed.objects.get(link=self.feed_url)

        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(new_feed.title, self.feedparser_dict['title'])
        self.assertEqual(
            new_feed.description,
            self.feedparser_dict['description']
        )
        self.assertEqual(new_feed.link, self.feed_url)
        self.assertEqual(new_feed.version, self.feedparser_dict['version'])

    def test_create_method(self):
        feed = Feed.objects.create(link=self.feed_url)
        self.assertTrue(self.mock_fetch_feedparser_dict.called)
        self.assertEqual(Feed.objects.count(), 1)

    def test_save_without_link_raises_error(self):
        feed = Feed()
        with self.assertRaises(TypeError):
            feed.save()
        self.assertEqual(Feed.objects.count(), 0)
        self.assertFalse(self.mock_fetch_feedparser_dict.called)

    def test_create_without_link_raises_error(self):
        with self.assertRaises(TypeError):
            feed = Feed.objects.create()
        self.assertEqual(Feed.objects.count(), 0)
        self.assertFalse(self.mock_fetch_feedparser_dict.called)

    def test_duplicate_feed_url_raises_validation_error(self):
        feed = Feed.objects.create(link=self.feed_url)
        with self.assertRaises(IntegrityError):
            Feed.objects.create(link=self.feed_url)

    def test_missing_feed_fields(self):
        del self.feedparser_dict['title']
        del self.feedparser_dict['description']
        del self.feedparser_dict['version']
        self.mock_fetch_feedparser_dict.return_value = self.feedparser_dict
        feed = Feed.objects.create(link=self.feed_url)

        self.assertEqual(feed.title, '')
        self.assertEqual(feed.description, '')
        self.assertEqual(feed.version, '')
