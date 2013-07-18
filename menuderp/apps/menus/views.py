from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from apps.menus import forms
import re


def SignupView(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = forms.SignupForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            email = form.cleaned_data['email']
            fname = form.cleaned_data['fname'].capitalize()
            lname = form.cleaned_data['lname'].capitalize()
            pword = form.cleaned_data['pword1']
            uname = re.split(r'@', email)[0]
            user = User.objects.create_user(uname, email, pword)
            user.first_name = fname
            user.last_name = lname
            user.save()
            return HttpResponseRedirect('/upsell/')  # Redirect after POST
    else:
        form = forms.SignupForm()  # An unbound form

    return render(request, 'menus/signup.html', {
        'form': form,
    })


def HomeView(request):
    return render(request, 'menus/home.html')


def AccountView(request):
    return render(request, 'menus/account.html')


def UpsellView(request):
    return render(request, 'menus/upsell.html')


def PayMeView(request):
    return render(request, 'menus/payme.html')
