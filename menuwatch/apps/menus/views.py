from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from apps.menus import forms
from apps.menus import models as menumods
from random import randint
from settings import common
from datetime import datetime, timedelta
import re

def IndexView(request):
    photo_num = randint(0,4)
    photo = str(photo_num)+".jpg"
    
    # YEAHHH I know, I'm storing data in a view. Sue me.
    # Also this is a fairly strange way to work around python's lack of switch statements
    # All in all, not one of the best code blocks I've ever written

    credits = {
        0: ("flic.kr/pinksherbet", "http://www.flickr.com/photos/pinksherbet/2316123291/"),
        1: ("flic.kr/ginnerobot", "http://www.flickr.com/photos/ginnerobot/2523448766/"),
        2: ("flic.kr/nomadic_lass", "http://www.flickr.com/photos/nomadic_lass/5846658416/"),
        3: ("flic.kr/giovannijl-s_photohut", "http://www.flickr.com/photos/giovannijl-s_photohut/459381964/"),
        4: ("flic.kr/clarity", "http://www.flickr.com/photos/clairity/1328402515/"),
    }

    name, link = credits.get(photo_num, (None,  None))
    
    authed = request.user.is_authenticated()
    return render(request, 'menus/index.html', {
        "photo": photo,
        "name": name,
        "link": link,
        "signedin": authed,
    })

def BrowseView(request):
    if request.user.is_authenticated():
        if 'sort' in request.GET and request.GET['sort'] == 'popular':
            context = {"foodlist": menumods.Food.objects.all().extra(order_by = ['-watch__food'])}
        elif 'sort' in request.GET and request.GET['sort'] == 'recent':
            context = {"foodlist": menumods.Food.objects.filter(last_date__gte=datetime.date(datetime.today()) - timedelta(days=2)).extra(order_by = ['-last_date'])}
        else:
            # default to showing ALL the foods!
            context = {"foodlist": menumods.Food.objects.all()}
        return render(request, 'menus/browse.html', context)
    else:
        return HttpResponseRedirect('/login/')

def LoginView(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/browse/')
    else:
        return render(request, 'menus/login.html')

def LogoutView(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect('/')

def SignupView(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/browse/')
    else:
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
                return HttpResponseRedirect('/browse/')  # Redirect after POST
        else:
            form = forms.SignupForm()  # An unbound form

        return render(request, 'menus/signup.html', {
            'form': form,
        })

def AccountView(request):
    if request.user.is_authenticated():
        return render(request, 'menus/account.html')
    else:
        return HttpResponseRedirect('/login/')

def UpgradeView(request):
    if request.user.is_authenticated():
        return render(request, 'menus/upgrade.html')
    else:
        return HttpResponseRedirect('/login/')

def ExcludeView(request):
    return render(request, 'menus/exclude.html')
