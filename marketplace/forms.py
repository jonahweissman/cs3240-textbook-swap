from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Profile

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
