from unittest.mock import patch

from django.db.utils import IntegrityError
from django.test import TestCase

from feeds.tests.helpers import (
    make_fake_feedparser_dict, make_feed_entries_list,
    make_preprocessed_entries_list
)
from feeds.models import Entry, Feed


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

    def test_feed_model_defaults(self):
        feed = Feed()
        self.assertEqual(feed.title, '')
        self.assertEqual(feed.description, '')
        self.assertEqual(feed.version, '')

    def test_feed_save_method(self):
        feed = Feed(link=self.feed_url)
        feed.save()
        new_feed = Feed.objects.get(link=self.feed_url)

        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(
            new_feed.title,
            self.feedparser_dict.feed['title']
        )
        self.assertEqual(
            new_feed.description,
            self.feedparser_dict.feed['description']
        )
        self.assertEqual(new_feed.link, self.feed_url)
        self.assertEqual(
            new_feed.version,
            self.feedparser_dict['version']
        )

    def test_create_method(self):
        feed = Feed.objects.create(link=self.feed_url)
        self.assertTrue(self.mock_fetch_feedparser_dict.called)
        self.assertEqual(Feed.objects.count(), 1)

    def test_updating_and_saving_existing_feed(self):
        feed = Feed.objects.create(link=self.feed_url)

        with patch.object(Feed, 'fetch_and_set_feed_details') as mock_fetch:
            # Modify values for existing feed and 
            # test that feed initialization no longer takes place
            my_feed = Feed.objects.get(link=feed.link)
            my_feed.title = 'New title'
            my_feed.description = 'New description'
            my_feed.save()
            self.assertFalse(mock_fetch.called)

        # Test if changes took effect
        this_feed = Feed.objects.get(link=feed.link)
        self.assertEqual(this_feed.title, 'New title')
        self.assertEqual(this_feed.description, 'New description')
        self.assertEqual(Feed.objects.count(), 1)

    def test_fetching_feed_details_method(self):
        feed = Feed(link=self.feed_url) # Instantiate, not save
        feed.fetch_and_set_feed_details()   # initialize, nopt saved
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(feed.title, self.feedparser_dict.feed['title'])
        self.assertEqual(
            feed.description,
            self.feedparser_dict.feed['description']
        )
        self.assertEqual(feed.version, self.feedparser_dict['version'])

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

    def test_duplicate_feed_url_raises_integrity_error(self):
        feed = Feed.objects.create(link=self.feed_url)
        with self.assertRaises(IntegrityError):
            # Creating a new Feed object
            # using a URL already in db
            Feed.objects.create(link=self.feed_url)

    def test_missing_feed_fields(self):
        del self.feedparser_dict.feed['title']
        del self.feedparser_dict.feed['description']
        del self.feedparser_dict['version']
        self.mock_fetch_feedparser_dict.return_value = self.feedparser_dict
        feed = Feed.objects.create(link=self.feed_url)

        self.assertEqual(feed.title, '')
        self.assertEqual(feed.description, '')
        self.assertEqual(feed.version, '')

    def test_feed_fetching_errors_interrupts_save(self):
        self.mock_fetch_feedparser_dict.side_effect = ValueError
        with self.assertRaises(ValueError):
            feed = Feed.objects.create(link=self.feed_url)

    def test_fetching_details_without_link(self):
        feed = Feed()
        with self.assertRaises(TypeError):
            feed.fetch_and_set_feed_details()


class EntryModelTest(TestCase):

    def test_field_defaults(self):
        entry = Entry.objects.create()
        self.assertEqual(Entry.objects.count(), 1)

    def test_back_reference(self):
        # Create some feeds
        feed_url1 = 'https://www.my-feeds.com/'
        feed_url2 = 'https://www.my-feeds2.com/'
        feed_url3 = 'https://www.my-feeds3.com/'

        feed_dict1 = make_fake_feedparser_dict(feed_url1)
        feed_dict2 = make_fake_feedparser_dict(feed_url2)
        feed_dict3 = make_fake_feedparser_dict(feed_url3)

        feed1 = None
        feed2 = None
        feed3 = None
        with patch('feeds.models.fetch_feedparser_dict') as mock_feed:
            mock_feed.side_effect = [feed_dict1, feed_dict2, feed_dict3]
            feed1 = Feed.objects.create(link=feed_url1)
            feed2 = Feed.objects.create(link=feed_url2)
            feed3 = Feed.objects.create(link=feed_url3)

        # Create an entry and assign to feeds 1 and 2
        entry = Entry.objects.create()
        feed1.entries.add(entry)
        feed2.entries.add(entry)

        self.assertEqual(entry.feeds.count(), 2)
        self.assertIn(feed1, entry.feeds.all())
        self.assertIn(feed2, entry.feeds.all())
        self.assertNotIn(feed3, entry.feeds.all())


@patch('feeds.models.preprocess_feed_entry_item')
@patch('feeds.models.fetch_feedparser_dict')
class EntryProcessingAndSavingTest(TestCase):

    def setUp(self):
        # Create a feed
        self.feed_url = 'https://www.my-feeds.com/'
        self.total_entries = 30
        self.feed_dict = make_fake_feedparser_dict(
            feed_url=self.feed_url,
            n_items=self.total_entries
        )
        self.feed = None
        with patch('feeds.models.fetch_feedparser_dict') as mock_feed:
            mock_feed.return_value = self.feed_dict
            self.feed = Feed.objects.create(link=self.feed_url)

        # Create list of processed entries
        self.parsed_entries = make_preprocessed_entries_list(
            n_items=self.total_entries,
            feed_url=self.feed_url
        )

    def test_entries_processing_and_saving(self, mock_fetch, mock_parse):
        mock_fetch.return_value = self.feed_dict
        mock_parse.side_effect = self.parsed_entries

        res = self.feed.update_feed_entries()
        self.assertEqual(self.feed.entries.count(), self.total_entries)
        self.assertEqual(res, self.total_entries)

    def test_errors_when_processing_entries(self, mock_fetch, mock_parse):
        mock_fetch.return_value = self.feed_dict
        self.parsed_entries[2] = IntegrityError
        self.parsed_entries[-1] = ValueError
        mock_parse.side_effect = self.parsed_entries

        res = self.feed.update_feed_entries()
        self.assertEqual(self.feed.entries.count(), self.total_entries - 2)
        self.assertEqual(res, self.total_entries - 2)

    def test_parsing_existing_entries(self, mock_fetch, mock_parse):
        mock_fetch.return_value = self.feed_dict
        mock_parse.side_effect = self.parsed_entries

        # Save two entries
        self.feed.entries.create(**self.parsed_entries[0])
        self.feed.entries.create(**self.parsed_entries[-1])

        res = self.feed.update_feed_entries()
        self.assertEqual(res, self.total_entries - 2)
        self.assertEqual(mock_parse.call_count, self.total_entries - 2)

    def test_old_entries_reached_limit(self, mock_fetch, mock_parse):
        mock_fetch.return_value = self.feed_dict
        mock_parse.side_effect = self.parsed_entries

        # Save all entries after the first 10 entries
        new_entries = 10
        for entry in self.parsed_entries[new_entries:]:
            self.feed.entries.create(**entry)

        res = self.feed.update_feed_entries()
        self.assertEqual(res, new_entries)
        self.assertEqual(mock_parse.call_count, new_entries)
