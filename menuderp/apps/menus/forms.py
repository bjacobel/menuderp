from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class SignupForm(forms.Form):
    email = forms.EmailField(max_length=50)
    fname = forms.CharField(max_length=50)
    lname = forms.CharField(max_length=50)
    pword1 = forms.CharField(widget=forms.PasswordInput)
    pword2 = forms.CharField(widget=forms.PasswordInput)

    def clean_pword2(self):
        pword1 = self.cleaned_data.get('pword1')
        pword2 = self.cleaned_data.get('pword2')

        if not pword2:
            raise forms.ValidationError("You must confirm your password")
        if pword1 != pword2:
            raise forms.ValidationError("Passwords do not match")
        return pword2

    def clean_email(self):
        if User.objects.filter(email = self.cleaned_data.get('email')).count():
            raise forms.ValidationError(mark_safe('A user with this email already exists. Did you mean to <a href="/login/">login</a>, or to <a href="/login#reset">reset your password</a>?'))