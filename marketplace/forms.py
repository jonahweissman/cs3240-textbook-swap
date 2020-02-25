from django import forms

from .models import Profile

class ImageForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields= ["imagefile"]

# class ImageForm(forms.Form):
#     imagefile = forms.ImageField(required=True)