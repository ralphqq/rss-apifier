from datetime import datetime
import pytz
import random
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from feedparser import FeedParserDict

from feeds.tests.helpers import make_fake_feedparser_dict
from feeds.utils.feed_tools import (
    clean_text, convert_to_utc, ENTRY_ITEM_FIELDS,
    fetch_feedparser_dict, preprocess_feed_entry_item
)


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

    def test_feed_has_entries_list(self, mock_parse):
        mock_parse.return_value = self.feedparser_dict
        feed = fetch_feedparser_dict(feed_url=self.feed_url)
        self.assertIn('entries', feed)
        self.assertIsInstance(feed['entries'], list)
        self.assertEqual(
            len(feed['entries']),
            len(self.feedparser_dict.entries)
        )

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


class ProcessEntryItemTests(TestCase):

    def setUp(self):
        self.feed_url = 'https://www.rssfeedstoday.com'
        self.feedparser_dict = make_fake_feedparser_dict(self.feed_url)
        self.feed_entries_list = self.feedparser_dict.entries
        self.entry_item = self.feed_entries_list[0]  # get a sample item

    @patch('feeds.utils.feed_tools.clean_text')
    @patch('feeds.utils.feed_tools.convert_to_utc')
    def test_valid_item_preprocessing(self, mock_utc, mock_clean):
        mock_utc.return_value = timezone.now()
        mock_clean.return_value = 'Cleaned text'
        item = preprocess_feed_entry_item(self.entry_item)

        # Check if transformationss are called
        self.assertTrue(mock_utc.called)
        self.assertTrue(mock_clean.called)

        # Check if output is valid
        self.assertIsInstance(item, dict)

        # Result must not contain unnecessary keys
        for result_key in item.keys():
            self.assertIn(result_key, ENTRY_ITEM_FIELDS)

    @patch('feeds.utils.feed_tools.clean_text')
    @patch('feeds.utils.feed_tools.convert_to_utc')
    def test_missing_required_fields_processing(self, mock_utc, mock_clean):
        mock_utc.return_value = timezone.now()
        mock_clean.return_value = 'Cleaned text'

        # randomly delete a required key
        del self.entry_item[random.choice(ENTRY_ITEM_FIELDS)]
        with self.assertRaises(TypeError):
            item = preprocess_feed_entry_item(self.entry_item)

        # Check if transformationss are not called
        self.assertFalse(mock_utc.called)
        self.assertFalse(mock_clean.called)

    def test_date_string_conversion(self):
        datetime_str = self.entry_item['published']
        datetime_utc = convert_to_utc(datetime_str)
        self.assertIsInstance(datetime_utc, datetime)
        self.assertEqual(datetime_utc.tzinfo, pytz.UTC)

    def test_html_tags_and_code_removal(self):
        raw_text = '<p>this&nbsp;&nbsp;string</p>'
        cleaned_text = clean_text(raw_text)
        self.assertEqual(cleaned_text, 'this  string')
