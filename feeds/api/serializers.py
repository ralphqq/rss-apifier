from rest_framework import serializers

from feeds.models import Entry, Feed


class EntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Entry
        fields = ['title', 'summary', 'published', 'link']


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    entries_list = serializers.HyperlinkedIdentityField(
        view_name='feed-entries',
        required=False
    )
    entries_count = serializers.SerializerMethodField(
        'count_entries',
        required=False
    )

    class Meta:
        model = Feed
        fields = [
            'id',
            'title',
            'description',
            'link',
            'version',
            'entries_count',
            'entries_list'
        ]
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'version': {'required': False},
        }

    def count_entries(self, feed):
        return feed.entries.count()
