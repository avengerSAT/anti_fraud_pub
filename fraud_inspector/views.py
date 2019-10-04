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
from check import sqlvertica 

import os
from datetime import datetime,timedelta

def filter_dan(gorod,start_time,end_time):
    if gorod=='ALL':
        FraudOrder=FraudOrders.objects.filter(order_date__range=(start_time,end_time))

    else:
        FraudOrder=FraudOrders.objects.filter(launch_region_id=gorod,order_date__range=(start_time,end_time))
    return FraudOrder

def blocked_unblocked(order_id,state):
    FraudOrders.objects.filter(order_id=order_id).update(state=state)
 
def check_city():
    City=apps.get_model('check','City')
    City=City.objects.all()
    return City


class Fraud_inspector(LoginRequiredMixin, View):
    def get(self,request):
        end_time= datetime.now().strftime('%Y-%m-%d')
        start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        City=check_city()
        gorod="ALL"
        FraudOrder=filter_dan(gorod,start_time,end_time)
        resol=["UNVERIFIED" ,"FRAUD YES","FRAUD NO"]
        return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                                        "end_time":end_time,
                                                                        "start_time":start_time,
                                                                        "gorod":gorod,
                                                                        "FraudOrder":FraudOrder,
                                                                        "resol":resol
        })
    def post(self,request):
         
        City=check_city()
        resol=["UNVERIFIED" ,"FRAUD YES","FRAUD NO"]
        try:
            block= request.POST["block"]
            resolution= request.POST["resolution"]
            gorod,order_id,start_time,end_time,pattern =block.split("///")
            state='UNBLOCKED'
            pattern=pattern.split(",")
            blocked_unblocked(order_id,state)
            FraudOrders.objects.filter(order_id=order_id).update(resolution=resolution)
            FraudOrder=filter_dan(gorod,start_time,end_time)
             
            return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                            "resol":resol,
                                                            "gorod":gorod,
                                                            "start_time":start_time,
                                                            "end_time":end_time,
                                                            "FraudOrder":FraudOrder
            })
        except:
            gorod= request.POST["kod_city"]
            start_time= request.POST["start_time"]
            end_time= request.POST["end_time"]
            FraudOrder=filter_dan(gorod,start_time,end_time) 
            return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                            "gorod":gorod,
                                                            "resol":resol,
                                                            "start_time":start_time,
                                                            "end_time":end_time,
                                                            "FraudOrder":FraudOrder
            })
@csrf_exempt 
def frod_prov(request):
    block= request.POST["block"]
    gorod,order_id,start_time,end_time,pattern =block.split("///")
    pattern=pattern.split(",")
    state='BLOCKED'
    resol=["UNVERIFIED" ,"FRAUD YES","FRAUD NO"]
    a=FraudOrders.objects.values_list('state', flat=True).filter(order_id=order_id)
    if str(a[0])==state:
        msg="Заказ проверяет другой пользователь"
        City=check_city()
        FraudOrder=filter_dan(gorod,start_time,end_time)
        return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                "gorod":gorod,
                                                "resol":resol,
                                                "msg":msg,
                                                "start_time":start_time,
                                                "end_time":end_time,
                                                "FraudOrder":FraudOrder    })
    blocked_unblocked(order_id,state)
    FraudOrder=FraudOrders.objects.filter(order_id=order_id)
    resol=[["UNVERIFIED","НЕ ПРОВЕРЕНО"],["FRAUD YES","ФРОД"],["FRAUD NO","НЕ ФРОД"]]
    driver_id,customer_id,drv_id=sqlvertica.sql_trip(order_id)
    chek_box='yes'
    cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus, time =\
        sqlvertica.sql_prov(customer_id, driver_id, drv_id, chek_box)
    PRV="1"
    return render (request,'fraud_inspector/Fraud_inspector.html',{"gorod":gorod,
                                                            "resol":resol,
                                                            "pattern":pattern,
                                                            "cus":cus,
                                                            "PRV":PRV,
                                                            "drv":drv,
                                                            "svod_drv_cus_head":svod_drv_cus_head,
                                                            "svod_drv_cus":svod_drv_cus,
                                                            "svod_cus_head":svod_cus_head,
                                                            "svod_cus":svod_cus,
                                                            "time":time,
                                                            "start_time":start_time,
                                                            "order_id":order_id,
                                                            "end_time":end_time,
                                                            "FraudOrder":FraudOrder

        })


class zagr_tr(LoginRequiredMixin, View):
    def get(self,request):
        end_time  = datetime.now().strftime('%Y-%m-%d')
        start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        City=check_city()
        gorod="ALL"
        return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                "gorod":gorod,
                                                                "end_time":end_time,
                                                                "start_time":start_time


        })



    def post (self,request):
        function=request.POST["function"]
        if function=="p_1":
            gorod= request.POST["kod_city"]
            start_time= request.POST["start_time"]
            end_time= request.POST["end_time"]
            update_db_fraud_orders(gorod,start_time,end_time)
            City=check_city()
            msg_1="Данные загружены"
            return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                    "end_time":end_time,
                                                                    "start_time":start_time,
                                                                    "gorod":gorod,
                                                                    "msg_1":msg_1
            })

        elif function=="p_2":
            trip_id= request.POST["trip_id"]
            end_time  = datetime.now().strftime('%Y-%m-%d')
            start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
            City=check_city()
            gorod="ALL"
            blocked_unblocked(trip_id,'UNBLOCKED')
            msg="Заказ разблокирован:"+trip_id
            return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                    "gorod":gorod,
                                                                    "end_time":end_time,
                                                                    "start_time":start_time,
                                                                    "msg":msg


    })





