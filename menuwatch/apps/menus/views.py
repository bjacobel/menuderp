from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from apps.menus import forms
from apps.menus import models as menumods
from random import randint
from hashlib import md5
from urllib import urlencode
import datetime
import operator


# god damn this file is getting massive


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
            # default to showing ALL the foods! (that are upcoming, at least)
            context = {"foodlist": sorted(menumods.Food.objects.all(), key=operator.attrgetter('peek_next_date'))}
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
    def send_verify_mail(request, new_user):
        template = loader.get_template('menus/email.html')
        context = RequestContext(request, {
            'first_name': new_user.first_name,
            'verify_link': "http://www.menuwat.ch/verify?" + urlencode({'e':new_user.email, 'v':md5(new_user.email).hexdigest()}),
            'unsubscribe_link': urlencode({'u':new_user.email, 't':md5(new_user.date_joined.isoformat()).hexdigest()}),
            'email_type': 'verify',
        })
        msg = EmailMultiAlternatives(
            "Menuwatch Signup Confirmation",
            "Hi, {}! Please visit this URL to finish setting up your account. {}".format(context['first_name'], context['verify_link']),
            "Menuwatch <mail@menuwat.ch>",
            ["{} {} <{}>".format(new_user.first_name, new_user.last_name, new_user.email),],
        )
        msg.attach_alternative(template.render(context), "text/html")
        msg.content_subtype = "html"
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
                new_user = User.objects.create_user(email, email, pword)
                new_user.first_name = fname
                new_user.last_name = lname
                new_user.is_active = False
                new_user.save()
                profile = menumods.Profile.objects.create(user_id=new_user.pk)
                profile.save()
                send_verify_mail(request, new_user)
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
            return HttpResponse("Request not authenticated", status=403)
    else:
        return HttpResponseRedirect('/')


@never_cache
@csrf_exempt
def AddView(request):
    if request.method == 'POST':  # api endpoint only accepts POSTs
        if request.user is not None:  # api should only work for signed-in users
            if 'food_pk' in request.POST:
                food = int(request.POST['food_pk'])
                user = int(request.user.pk)
                if menumods.Profile.objects.get(user__exact=user).can_create_new_watches():
                    try:
                        menumods.Watch.objects.create(food=menumods.Food.objects.get(pk__exact=food), owner=menumods.Profile.objects.get(user__exact=user))
                        return HttpResponse("Watch successfully created", status=201)
                    except:
                        return HttpResponse("Specified food does not exist", status=404)
                else:
                    return HttpResponse("Watch limit reached", status=431)  # 'server is unwilling to process the request' UNTIL YOU PAY ME MONIES
            else:
                return HttpResponse("No food_pk specified", status=400)
        else:
            return HttpResponse("No authenticated user present", status=403)
    else:
        return HttpResponse("I'm a teapot", status=418)


@never_cache
@csrf_exempt
def DeleteView(request):
    if request.method == 'POST':
        if request.user is not None:
            if 'food_pk' in request.POST:
                food = int(request.POST['food_pk'])
                user = int(request.user.pk)
                try:
                    watch = menumods.Watch.objects.get(food__exact=food, owner__exact=menumods.Profile.objects.get(user__exact=user))
                    watch.delete()
                    return HttpResponse("Watch successfully deleted", status=200)
                except:
                    return HttpResponse("No watch mathing those parameters found", status=404)
            else:
                return HttpResponse("No food_pk specified", status=400)
        else:
            return HttpResponse("No authenticated user present", status=403)
    else:
        return HttpResponse("I'm a teapot", status=418)

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
