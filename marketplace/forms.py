from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from .models import Profile, Item
from . import models

class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
        ]
class ImageForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields= ["imagefile" ,"phonenumber", "major", "year"]

class ItemForm(forms.ModelForm):
    class Meta:
        model= Item
        fields= ["item_image"]


class SendMessageForm(forms.Form):
    text = forms.CharField(strip=True,
                           error_messages={'required': "Type a message"},
                           label='')
    to = forms.ModelChoiceField(queryset=models.Profile.objects.all(),
        widget=forms.HiddenInput)
    conversation = forms.ModelChoiceField(
        queryset=models.Conversation.objects.all(),
        widget=forms.HiddenInput)
    in_response_to = forms.ModelChoiceField(queryset=models.Message.objects.all(),
        widget=forms.HiddenInput)
