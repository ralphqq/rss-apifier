from django.forms import ModelForm


from .models import Feed


class FeedAdminAddForm(ModelForm):

    class Meta:
        model = Feed
        fields = ['link']


class FeedAdminChangeForm(ModelForm):

    class Meta:
        model = Feed
        fields = ['link', 'title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['link'].required = True
        self.fields['title'].required = False
        self.fields['description'].required = False
