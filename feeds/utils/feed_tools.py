import feedparser

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
    if not feed or not feed.get('version') or feed.get('bozo'):
        raise ValueError('Invalid or unrecognized feed format')
    return feed
