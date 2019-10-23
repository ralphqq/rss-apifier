from feedparser import FeedParserDict


def make_fake_feedparser_dict(feed_url):
    """Creates a fake but valid FeedParserDict object."""
    return FeedParserDict(
        title='Sample Feed',
        description='This is a sample feed',
        link=feed_url,
        version='rss20',
        bozo=0,
    )
