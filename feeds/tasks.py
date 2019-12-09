import logging

from celery import shared_task

from .models import Feed


@shared_task(name='fetch-entries')
def fetch_entries():
    """Fetches and saves all new entries for each RSS feed in the db.

    Returns:
        int: count of all RSS entries successfully saved
    """
    logging.info('Fetching new RSS entries')
    feeds = Feed.objects.all()

    if feeds.exists():
        logging.info(f'Found {feeds.count()} total RSS feeds to process')

        total_entries_saved = 0
        for feed in feeds:
            try:
                entries_saved = feed.update_feed_entries()
            except Exception as e:
                logging.error(e)
            else:
                logging.info(
                    f'Saved {entries_saved} new entries from {feed.link}'
                )
                total_entries_saved += entries_saved

        logging.info(f'Processed and saved a total of {total_entries_saved} new RSS Entries')
        return total_entries_saved

    else:
        logging.warning('No RSS feeds found in the database')
