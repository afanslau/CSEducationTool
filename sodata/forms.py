from django import forms
from django.contrib.auth.models import User
from sodata.models import Resources

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
    # def __init__(self):
    #     self.fields['text'].widget=forms.Textarea
    text_input_css_class = 'form-control flat-input'


    title = forms.CharField(widget=forms.TextInput(attrs={'class':text_input_css_class}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class':text_input_css_class}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class':text_input_css_class,'rows':3}))
    class Meta:
        model = Resources
        fields = ('title','url','text')
    # title = forms.CharField()
    # url = forms.URLField()
    # text = forms.CharField(widget=forms.Textarea)

    # Should the save override logic go in form validation? I want it to verify during saves also