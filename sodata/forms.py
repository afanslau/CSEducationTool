from urlparse import urlparse
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from sodata.models import Resources
from django.core import validators
from django.core.exceptions import ValidationError
import re



class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(widget=forms.TextInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, we couldn't match that username and password. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user

# class LoginForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())

#     class Meta:
#         model = User
#         fields = ('username', 'password')


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ('website', 'picture')

class ResourceForm(forms.ModelForm):
    # def __init__(self):
    #     self.fields['text'].widget=forms.Textarea
    text_input_css_class = 'form-control flat-input'

    id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':text_input_css_class}))
    url = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':text_input_css_class}))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':text_input_css_class}))
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':text_input_css_class,'rows':3}))
    

    # Use for save to form
    # profile = forms.ModelChoiceField(queryset=Profile.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Resources
        fields = ('id','title','url','tags','text')

    # Custom validation http://stackoverflow.com/questions/7948750/custom-form-validation
    # def clean_fieldname(self):
    # def clean(self):
    #     form_data = self.cleaned_data
    #     if form_data['password'] != form_data['password']:
    #         self._errors["password"] = ["Password do not match"] # Will raise a error message
    #         del form_data['password']
    #     return form_data

    def clean_url(self):
        _url = self.cleaned_data.get('url')
        if _url == '':
            return None

        parse_result = urlparse(_url)
        if parse_result.netloc == '': #No http was provided
            _url = 'http://'+parse_result.geturl()
            parse_result = urlparse(_url)
        return _url 

    def clean_title(self):
        _title = self.cleaned_data.get('title')
        if _title == '':
            return None
        return _title

    def clean_text(self):
        _text = self.cleaned_data.get('text')
        if _text == '':
            return None
        return _text



    def clean(self):
        form_data = self.cleaned_data
        
        # Check that at least one field is present
        valid_so_far = False
        for k in ['title','text','url']:
            d = form_data[k]
            if d is not None:
                valid_so_far = True
                break
        if not valid_so_far:
            raise forms.ValidationError(u"A resource cannot be blank. Please fill out at least one field")
        
        tags = form_data.get('tags',None)

        print 'form clean:  ', tags

        if tags is not None:
            # Split by commas or spaces
            form_data['tags'] = re.split('\s*,*\s*', tags)

        return form_data







# Source:  https://gist.github.com/eerien/7002396

# class MinLengthValidator(validators.MinLengthValidator):
#     message = 'Ensure this value has at least %(limit_value)d elements (it has %(show_value)d).'
 
# class MaxLengthValidator(validators.MaxLengthValidator):
#     message = 'Ensure this value has at most %(limit_value)d elements (it has %(show_value)d).'
 
 
# class CommaSeparatedCharField(forms.Field):
#     def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
#         self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
#         super(CommaSeparatedCharField, self).__init__(*args, **kwargs)
#         if min_length is not None:
#             self.validators.append(MinLengthValidator(min_length))
#         if max_length is not None:
#             self.validators.append(MaxLengthValidator(max_length))
 
#     def to_python(self, value):
#         if value in validators.EMPTY_VALUES:
#             return []
 
#         value = [item.strip() for item in value.split(',') if item.strip()]
#         if self.dedup:
#             value = list(set(value))
 
#         return value
 
#     def clean(self, value):
#         value = self.to_python(value)
#         self.validate(value)
#         self.run_validators(value)
#         return value
    # title = forms.CharField()
    # url = forms.URLField()
    # text = forms.CharField(widget=forms.Textarea)

    # Should the save override logic go in form validation? I want it to verify during saves also