from django.views.decorators.csrf import csrf_exempt, csrf_protect,requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,render_to_response,redirect
from django.template import loader, Context
from django.http import HttpResponse
from django.contrib import auth
from django.views import View

from .models import FraudOrders
from  django.apps  import apps

 

import os

 



class zagr_tr(LoginRequiredMixin, View):
    def get(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        print(City)
        return render (request,'fraud_inspector/zagr.html',{"City":City
        })
    def post(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        gorod= request.POST["kod_city"]
        return render (request,'fraud_inspector/zagr.html',{"City":City,
                                                           "gorod":gorod
        })

class Fraud_inspector(LoginRequiredMixin, View):
    def get(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        print(City)
        return render (request,'fraud_inspector/zagr.html',{"City":City
        })
    def post(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        gorod= request.POST["kod_city"]
        return render (request,'fraud_inspector/zagr.html',{"City":City,
                                                           "gorod":gorod
        })