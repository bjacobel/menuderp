from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.template import Context, loader
import re


def SignupView(request):
    return render(request, 'menus/signup.html')
