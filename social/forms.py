from django import forms

from social.models import Usernames

class PostForm(forms.ModelForm):

    class Meta:
        model = Usernames
        fields = ('username',)