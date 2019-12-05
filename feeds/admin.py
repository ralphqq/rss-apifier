from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from feeds.forms import FeedAdminAddForm, FeedAdminChangeForm
from feeds.models import Feed


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'version', 'link']
    form = FeedAdminAddForm

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Ensures errors are handled when submitting forms in admin.

        Adapted from Stack Overflow answer:
        https://stackoverflow.com/a/39512190
        """
        try:
            response = super().changeform_view(request, object_id, form_url, extra_context)
        except Exception as e:
            self.message_user(request, e, level=messages.ERROR)
            return HttpResponseRedirect(form_url)
        return response

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            return FeedAdminChangeForm
        else:
            return super().get_form(request, obj, **kwargs)
