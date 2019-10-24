from django.contrib import admin

from feeds.models import Feed


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'version', 'link']
    fields = ['link']
