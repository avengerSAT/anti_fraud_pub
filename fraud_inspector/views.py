from django.views.decorators.csrf import csrf_exempt, csrf_protect,requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,render_to_response,redirect
from django.template import loader, Context
from django.http import HttpResponse
from django.contrib import auth
from django.views import View


 

import os

 



   