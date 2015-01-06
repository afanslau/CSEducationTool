from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ('website', 'picture')

class ResourceForm(forms.ModelForm):
    def __init__(self):
        self.fields['text'].widget=forms.Textarea
    class Meta:
        fields = ('title','url','text')
    # title = forms.CharField()
    # url = forms.URLField()
    # text = forms.CharField(widget=forms.Textarea)

    # Should the save override logic go in form validation? I want it to verify during saves also