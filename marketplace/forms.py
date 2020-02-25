from django import forms

from .models import Profile

class ImageForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields= ["imagefile" ,"phonenumber", "major", "year"]

# class ImageForm(forms.Form):
#     imagefile = forms.ImageField(required=True)