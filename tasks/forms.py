# from django import forms
# from .models import LinkedInAccount
# # from user.models import signup_view
# # from user.models import Signup
#
# class LinkedInAccountForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)  # Password input field
#
#     class Meta:
#         model = LinkedInAccount
#         fields = ['email', 'password', 'profile_name']
# # forms.py
#
# class LinkedInLoginForm(forms.Form):
#     email = forms.EmailField(label="LinkedIn Email", required=True)
#     password = forms.CharField(label="LinkedIn Password", widget=forms.PasswordInput, required=True)
#

# class SignupForm(forms.ModelForm):
#     class Meta:
#         # Import Signup only when needed
#
#         model = Signup
#         fields = ['email', 'password', 'name']

from django import forms
from .models import LinkedInAccount
from .models import LeadList

class LinkedInLoginForm(forms.Form):
    email = forms.EmailField(label="LinkedIn Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="LinkedIn Password")

class LinkedInAccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Password input field

    class Meta:
        model = LinkedInAccount
        fields = ['email', 'password', 'profile_name']


class LeadListForm(forms.ModelForm):
    class Meta:
        model = LeadList
        fields = ['name', 'source_url', 'import_csv_file']