from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
import re

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


class EmailProfileField(forms.Field):
    '''extract email from "name <name@example.com>"'''
    def clean(self, value):
        email_re = re.compile(r'<(.+@.+\..+)>')
        email = email_re.search(value)
        if email is None:
            raise forms.ValidationError
        email = email.group(1)
        from_user = models.User.objects.filter(email=email)[0]
        return from_user.profile


class EmailUuidField(forms.Field):
    '''extract uuid from "name <name+uuid@example.com>"'''
    def clean(self, value):
        uuid_re = re.compile(r'\+(.*?)@')
        uuid = uuid_re.search(value)
        if uuid is None:
            raise forms.ValidationError
        uuid = uuid.group(1)
        in_response_to = models.Message.objects.get(pk=uuid)
        return in_response_to


class ReceiveMessageForm(forms.ModelForm):
    '''process emails from CloudMailIn'''
    author = EmailProfileField()
    in_response_to = EmailUuidField()
    conversation = forms.ModelChoiceField(
        queryset=models.Conversation.objects.all(),
        required=False)

    class Meta:
        model = models.Message
        fields = ['author', 'in_response_to', 'conversation', 'text']

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['conversation'] = cleaned_data['in_response_to'].conversation
        return cleaned_data


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
