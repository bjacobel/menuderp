from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from apps.menus import forms
from apps.menus import models as menumods
from random import randint
from hashlib import md5
from urllib import urlencode
import requests
import operator
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
            context = {"foodlist": sorted(menumods.Food.objects.all(), key=operator.attrgetter("num_watches"))[:30]}
        elif 'sort' in request.GET and request.GET['sort'] == 'recent':
            context = {"foodlist": menumods.Food.objects.order_by('-last_date')[:30]}
        else:
            # default to showing ALL the foods!
            context = {"foodlist": menumods.Food.objects.all()}
        return render(request, 'menus/browse.html', context)
    else:
        return HttpResponseRedirect('/login')


def LoginView(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/browse')
    else:
        if request.method == 'POST':  # If the form has been submitted...
            form = forms.LoginForm(request.POST)  # A form bound to the POST data
            if form.is_valid():  # All validation rules pass
                email = form.cleaned_data['email']
                pword = form.cleaned_data['pword']
                user = authenticate(username=email, password=pword)
                if user is not None and user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/browse')  # Redirect after POST
                else:
                    return HttpResponseRedirect('/login')  # Redirect after POST
        else:
            form = forms.LoginForm()  # An unbound form

        return render(request, 'menus/auth.html', {
            'form': form,
            'action': 'login',
            'button_text': "LOG IN",
            'other_action': 'signup',
            'other_button_text': "sign up",
        })


def SignupView(request):
    def send_verify_mail(user, link):
        msg = EmailMessage(
            subject="Menuwatch Signup Confirmation",
            from_email="Menuwatch <mail@menuwat.ch>",
            to=["{} {} <{}>".format(user.first_name, user.last_name, user.email),],
        )
        msg.template_content = {}
        msg.template_name = "signup-verification"
        msg.global_merge_vars = {
            'FNAME': user.first_name,
            'LINK': link,
            'UNSUB': urlencode({'u':user.email, 't':md5(user.date_joined.isoformat()).hexdigest()}),
        }
        msg.send()

    if request.user.is_authenticated():
        return HttpResponseRedirect('/browse')
    else:
        if request.method == 'POST':  # If the form has been submitted...
            form = forms.SignupForm(request.POST)  # A form bound to the POST data
            if form.is_valid():  # All validation rules pass
                email = form.cleaned_data['email']
                fname = form.cleaned_data['fname'].capitalize()
                lname = form.cleaned_data['lname'].capitalize()
                pword = form.cleaned_data['pword1']
                user = User.objects.create_user(email, email, pword)
                user.first_name = fname
                user.last_name = lname
                user.is_active = False
                user.save()
                profile = menumods.Profile.objects.create(user_id=user.pk)
                profile.save()
                verify_link = "http://www.menuwat.ch/verify?" + urlencode({'e':email, 'v':md5(email).hexdigest()})
                send_verify_mail(user, verify_link)
                return HttpResponseRedirect('/verify')  # Redirect after POST
        else:
            form = forms.SignupForm()  # An unbound form

        return render(request, 'menus/auth.html', {
            'form': form,
            'action': 'signup',
            'button_text': "SIGN UP",
            'other_action': 'login',
            'other_button_text': "log in",
        })


def VerifyView(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/login')
    elif request.GET and 'e' in request.GET and 'v' in request.GET:
        email = request.GET['e']
        emailhash = request.GET['v']
        if md5(email).hexdigest() == emailhash:
            to_verify = User.objects.get(username__exact=email)
            to_verify.is_active=True
            to_verify.save()
        return HttpResponseRedirect('/login')
    else:
        return render(request, 'menus/verify.html')


def AccountView(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login')
    else:
        context = {
            "profile": menumods.Profile.objects.get(user__exact=request.user.pk),
            'unsub_link': urlencode({'u':request.user.email, 't':md5(request.user.date_joined.isoformat()).hexdigest()}),
        }
        return render(request, 'menus/account.html', context)


def ChangePasswordView(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login')
    else:
        if request.method == 'POST':  # If the form has been submitted...
            form = forms.ChangePasswordForm(request.POST)  # A form bound to the POST data
            if form.is_valid():  # All validation rules pass
                old_pword = form.cleaned_data['pword0']
                new_pword = form.cleaned_data['pword1']
                if authenticate(username=request.user.email, password=old_pword):
                    u = User.objects.get(username__exact=request.user.email)
                    u.set_password(new_pword)
                    u.save()
                    return HttpResponseRedirect('/account')
                else:
                    return HttpResponseRedirect('/account/password')
        else:
            form = forms.ChangePasswordForm()  # An unbound form

        return render(request, 'menus/auth.html', {
            'form': form,
            'action': 'account/password',
            'button_text': "CHANGE",
            'other_action': 'account',
            'other_button_text': "go back",
        })    


def UpgradeView(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login')
    else:
        context = { "popular" : sorted(menumods.Food.objects.all(), key=operator.attrgetter("num_watches"))[:10]}
        return render(request, 'menus/upgrade.html', context)


def UnsubView(request):
    if 'u' in request.GET and 't' in request.GET:
        # need to pass a plaintext username and the MD5hashed signup date of that user
        # so you can't just randomly unsubscribe people... that would be funny
        user = request.GET['u'] 
        if md5(User.objects.get(email__exact=user).date_joined.isoformat()).hexdigest() == request.GET['t']:
            User.objects.get(email__exact=user).delete()
            return render(request, 'menus/unsubscribe.html')
        else:
            return HttpResponseServerError()
    else:
        return HttpResponseRedirect('/')


@csrf_exempt
def AddView(request):
    if request.method == 'POST':  # api endpoint only accepts POSTs
        if request.user is not None:  # api should only work for signed-in users
            if 'pk' in request.GET:
                food = request.GET['pk']
                user = request.user.pk
                watch = menumods.Watch.create(food=food, owner=user)
                watch.save()
    return HttpResponseServerError()


@csrf_exempt
def DeleteView(request):
    if request.method == 'POST':  # api endpoint only accepts POSTs
        if request.user is not None:  # api should only work for signed-in users
            if 'pk' in request.GET:
                food = request.GET['pk']
                user = request.user.pk
                watch = menumods.Watch.objects.get(food__exact=food, owner__exact=user)
                watch.delete()
    return HttpResponseServerError()

def LogoutView(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect('/')


def PaymentView(request):
    return render(request, 'menus/payment.html')


def ExcludeView(request):
    return render(request, 'menus/exclude.html')


def AboutView(request):
    return render(request, 'menus/about.html')
