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
from .import_data import update_db_fraud_orders
 

import os
 



class zagr_tr(LoginRequiredMixin, View):
    def get(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        a=FraudOrders.objects.filter(order_id='00169d2d-d4c5-46bc-b651-8e5c8db9fad1')
        print(a[0])
        return render (request,'fraud_inspector/zagr.html',{"City":City
        })
    def post(self,request):
        update_db_fraud_orders()
        gorod= request.POST["kod_city"]
        start_time= request.POST["start_time"]
        end_time= request.POST["end_time"]
        City=apps.get_model('check','City')
        City=City.objects.all()
 #       FraudOrder=FraudOrders.objects.filter(order_date__range=(start_time,end_time))
        print(start_time,end_time)
        return render (request,'fraud_inspector/zagr.html',{"City":City,
                                                           "gorod":gorod,
                                                           "start_time":start_time,
                                                           "end_time":end_time,
   #                                                        "FraudOrder":FraudOrder
        })

class Fraud_inspector(LoginRequiredMixin, View):
    def get(self,request):
        City=apps.get_model('check','City')
        City=City.objects.all()
        FraudOrders=FraudOrders.objects.all()
        return render (request,'fraud_inspector/zagr.html',{"City":City,
                                                            "FraudOrders":FraudOrders
        })
    def post(self,request):
        gorod= request.POST["kod_city"]
        City=apps.get_model('check','City')
        City=City.objects.all()
        FraudOrders=FraudOrders.objects.all()
        return render (request,'fraud_inspector/zagr.html',{"City":City,
                                                            "gorod":gorod,
                                                            "FraudOrders":FraudOrders
        })


        
