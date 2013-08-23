from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
import re

class SignupForm(forms.Form):
    fname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    lname = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    pword1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    pword2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password, again'}))

    def clean_pword1(self):
        pword1 = self.cleaned_data.get('pword1')
        if len(pword1) < 6:
            raise forms.ValidationError("Your password must be at least six characters")
        return pword1

    def clean_pword2(self):
        pword1 = self.cleaned_data.get('pword1')
        pword2 = self.cleaned_data.get('pword2')

        if pword1 != pword2:
            raise forms.ValidationError("Passwords do not match")
        return pword2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email = email).count():
            raise forms.ValidationError(mark_safe('A user with this email already exists. Did you mean to <a href="/login/">login</a>, or to <a href="/login#reset">reset your password</a>?'))
        return email

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    pword = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))