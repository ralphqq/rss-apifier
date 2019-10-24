from unittest.mock import patch

from django.test import TestCase
from feedparser import FeedParserDict

from feeds.tests.helpers import make_fake_feedparser_dict
from feeds.utils.feed_tools import fetch_feedparser_dict


@patch('feeds.utils.feed_tools.feedparser.parse')
class FetchFeedParserDictTest(TestCase):

    def setUp(self):
        self.feed_url = 'https://www.samplefeeds.com/rss'   # fake URL

        # Create and set a valid FeedParserDict object
        # to be used or overridden in the tests
        self.feedparser_dict = make_fake_feedparser_dict(self.feed_url)

    def test_returns_feedparser_dict_object(self, mock_parse):
        mock_parse.return_value = self.feedparser_dict
        feed = fetch_feedparser_dict(feed_url=self.feed_url)
        self.assertTrue(mock_parse.called)
        self.assertIsInstance(feed, FeedParserDict)
        self.assertIn('feed', feed) # details dict is in parse result

    def test_null_feedparser_object_raises_error(self, mock_parse):
        self.feedparser_dict = None
        mock_parse.return_value = self.feedparser_dict
        with self.assertRaises(ValueError):
            fetch_feedparser_dict(self.feed_url)

    def test_unknown_rss_version_raises_error(self, mock_parse):
        self.feedparser_dict['version'] = ''
        mock_parse.return_value = self.feedparser_dict
        with self.assertRaises(ValueError):
            fetch_feedparser_dict(self.feed_url)

    def test_badly_formed_feed_raises_error(self, mock_parse):
        self.feedparser_dict['bozo'] = 1
        mock_parse.return_value = self.feedparser_dict
        with self.assertRaises(ValueError):
            fetch_feedparser_dict(self.feed_url)

    def test_missing_feed_details_dict_raises_error(self, mock_parse):
        del self.feedparser_dict['feed']
        mock_parse.return_value = self.feedparser_dict
        with self.assertRaises(ValueError):
            fetch_feedparser_dict(self.feed_url)
