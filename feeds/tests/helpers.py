from datetime import datetime, timedelta
import random
from urllib.parse import urljoin

from feedparser import FeedParserDict


def make_fake_feedparser_dict(feed_url, n_items=30):
    """Creates a fake but valid FeedParserDict object.

    Args:
        feed_url (str): Fake URL for fake Feed
        n_items (int): number of fake entries to generate
    """
    return FeedParserDict(
        feed=FeedParserDict(
            title='Sample Feed',
            description='This is a sample feed',
            link=feed_url
        ),
        entries=make_feed_entries_list(
            n_items=n_items,
            feed_url=feed_url
        ),
        version='rss20',
        bozo=0,
    )


def make_feed_entries_list(n_items=10, feed_url=''):
    """Generates a list of feed entries.

    Args:
        n_items (int): how many feed entries to make
        feed_url (str): base URL
    """
    tz = ['+0800', 'GMT']
    fmt = '%a, %d %b %Y %H:%M:%S'
    now = datetime.now()
    offset = timedelta(minutes=1)
    return [
        FeedParserDict(
            link=urljoin(feed_url, f'story-{i + 1:05d}.html'),
            published=(
                f'{(now - offset * random.randint(1, 180)).strftime(fmt)} '
                f'{random.choice(tz)}'
            ),
            author=f'Author {i + 1}',
            summary=f'Summary {i + 1}',
            title=f'Title {i + 1}'
        ) for i in range(n_items)
    ]
