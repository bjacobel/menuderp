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
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email = email).count():
            raise forms.ValidationError(mark_safe('A user with this email already exists. Did you mean to <a href="/login">login</a>, or to <a href="/reset">reset your password</a>?'))
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    pword = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email = email).count():
            raise forms.ValidationError(mark_safe('We don\'t have any users with that email address. Did you mean to <a href="/signup">sign up</a>?'))
        return email

    def clean_pword(self):
        email = self.cleaned_data.get('email')
        pword = self.cleaned_data.get('pword')
        if User.objects.filter(email = email).count() == 1:
            u = User.objects.filter(email = email)[:1].get()
            if not u.check_password(pword):
                raise forms.ValidationError(mark_safe('Incorrect password. If you forgot, you can request a <a href="/reset">password reset</a>.'))
        return pword


class RequestResetForm(forms.Form):
    email = forms.EmailField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Email'}))

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email = email).count():
            raise forms.ValidationError(mark_safe('We don\'t have any users with that email address. <a href="/signup">Sign up</a> for a new account?'))
        return email


class ProcessResetForm(forms.Form):
    pword1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    pword2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password, again'}))

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

class ChangePasswordForm(forms.Form):
    pword0 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Old password'}))
    pword1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    pword2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password, again'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_pword0(self):
        pword0 = self.cleaned_data.get('pword0')
        if not self.user.check_password(pword0):
            raise forms.ValidationError("Incorrect old password")
        return pword0

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