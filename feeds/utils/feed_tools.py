from dateutil import parser
from django.utils import timezone
from django.utils.html import strip_tags
import feedparser
import pytz

# Required entry item fields
ENTRY_ITEM_FIELDS = [
    'link',
    'published',
    'summary',
    'title',
]


def fetch_feedparser_dict(feed_url):
    """Fetches feed details from given URL.

    Returns:
        feedparser.FeedParserDict object, see:
            https://pythonhosted.org/feedparser/

    Raises:
        ValueError: if the URL points to an unrecognized or invalid 
            RSS or Atom format
    """
    feed = feedparser.parse(feed_url)
    if (not feed or not feed.get('version') or 
            feed.get('bozo') or 'feed' not in feed):
        raise ValueError('Invalid or unrecognized feed format')
    return feed


def preprocess_feed_entry_item(entry_item):
    """Makes an entry item ready for saving into database.

    This function applies the following operations to the given entry item:
    1. Checks if all required fields are present
    2. Converts published date into tz-aware datetime object (UTC)
    3. Removes any HTML tags from values
    4. Excludes any unnecessary fields

    Args:
        entry_item (FeedParserDict): the entry item to be processed

    Returns:
        dict: dictionary containing the processed values
    """
    for field in ENTRY_ITEM_FIELDS:
        if field not in entry_item:
            raise TypeError('{field} not found in feed entry item')

    return {
        'link': entry_item['link'],
        'published': convert_to_utc(entry_item['published']),
        'summary': clean_text(entry_item['summary']),
        'title': clean_text(entry_item['title'])
    }


def convert_to_utc(published):
    """Parses datetime string and converts it to tz-aware datetime."""
    try:
        published_dt = parser.parse(published)
        return published_dt.astimezone(pytz.UTC)
    except Exception as e:
        return timezone.now()


def clean_text(text):
    """Removes HTML tags and entities from given text."""
    no_html_tags = strip_tags(text)
    return no_html_tags.replace('&nbsp;', ' ')
