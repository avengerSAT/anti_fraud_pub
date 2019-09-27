import csv
import gzip
import os
import threading
import time
from datetime import datetime, timedelta
import jinja2
import numpy as np
import pandas as pd
import tablib
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response
from django.template import Context, loader
from django.utils.decorators import method_decorator
from django.views import View

import threading
from datetime import datetime,timedelta
from django.views.decorators.csrf import (csrf_exempt, csrf_protect,
                                          requires_csrf_token)
from isoweek import Week


from . import import_bd, import_csv, sqlvertica
from .models import City
from .dash_.dash_1 import dispatcher



def creatFolder(user_temp):
    if not os.path.exists(user_temp):
        os.mkdir(user_temp)
    
 


def puti(username):
    trail="check/templates/csv"+username
    trail_m="media/media_"+username  
    trail_pd="templates/csv"+username
    creatFolder(trail)
    creatFolder(trail_m)
    return  trail,trail_pd


class time_serv():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S ')
    now_D_1 = (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
    now_D_2 = (datetime.now()- timedelta(days=2)).strftime('%Y-%m-%d')
    timem =datetime.now()-timedelta(days=7)
    time_d=timem.strftime('%Y-%m-%d %H:%M:%S ')



class MAIN(LoginRequiredMixin, View):
    def get(self,request):
        trail,trl=puti(request.user.username ) 
        return render (request,'check/prover.html')
    def post(self,request):
        return render (request,'check/prover.html')


class Fraud_PROV(LoginRequiredMixin, View):
    def get(self,request):
        trail,trl=puti(request.user.username ) 
        return render (request,'check/test_prover.HTML')
    def post(self,request):
        trip_id = request.POST["trip_id"]
        chek_box = request.POST.get("chek_box")
        driver_id,customer_id,drv_id=sqlvertica.sql_trip(trip_id)
        if chek_box=='yes':
            cus_head,cus,drv_hed,drv,svod_cus_head ,svod_cus,svod_drv_cus_head,svod_drv_cus=sqlvertica.sql_prov(customer_id,driver_id,drv_id,chek_box)
            chek_box='checked'
        else:
            chek_box=''
            cus_head,cus,drv_hed,drv,svod_cus_head ,svod_cus,svod_drv_cus_head,svod_drv_cus=sqlvertica.sql_prov(customer_id,driver_id,drv_id,chek_box)
        
        return render (request,'check/test_prover.HTML',{"cus":cus,
                                                    "drv":drv,
                                                    "box_c":chek_box,
                                                    "svod_drv_cus_head":svod_drv_cus_head,
                                                    "svod_drv_cus":svod_drv_cus,
                                                    "svod_cus_head":svod_cus_head,
                                                    "svod_cus":svod_cus})     

class Driver(LoginRequiredMixin, View):
    def get(self,request):
        trail,trl=puti(request.user.username ) 
        data="нет данных"
        return render(request,'check/Driver.html' ,{"data":data})

    @csrf_exempt 
    def post(self,request): 
        trip_id = request.POST['trip_id']  
        trail,trl=puti(request.user.username ) 
        driver_id,customer_id,drv_id=sqlvertica.sql_trip(trip_id)
        sqlvertica.sql_old_drv(drv_id,trail)
        return redirect("/check/Driver/1/")    


def drvr(request):
    try:
        trail,trl=puti(request.user.username ) 
        a= trail+'/Сводная_по_водителю.csv'
        df=pd.read_csv(a)
        try:
            df[['Дуэт','Кол поездок клиента']] = df[['Дуэт','Кол поездок клиента']].astype('int')
            df['Доля совместных поездок']=df['Дуэт']/df['Кол поездок клиента']*100
            df['Доля совместных поездок']=df['Доля совместных поездок'].astype('str')+" %"
        except:  
            df['Доля совместных поездок']=df['Дуэт']  
        df['Стасус']=df['Стасус']+" / "+df['Статус р'] 
        if request.method == 'POST':
            sort_id = request.POST['sort_id']
            if sort_id =="":
                dw=df[['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']]
                dw=dw.drop_duplicates()
                dw.to_csv(trail+'/Сводная_по_водителю2.csv',index=False)
                with open(trail+'/Сводная_по_водителю2.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    data2 = list(zip(*rows))        
                test=['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']                    
                de=df[test]
                de=de.sort_values(['Дуэт'], ascending=[False])
                de=de.drop_duplicates()
                de.to_csv(trail+'/Сводная_по_водителю3.csv',index=False, header=False)
                with open(trail+'/Сводная_по_водителю3.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    dee = list(rows)
                return render(request,'check/Driver.html' ,{"data2":data2,
                                                                "de":test,
                                                                "dee":dee
                                                                }) 
            else:
                b=df.loc[(df['ИД поездки'] == sort_id ) | (df['ИД клиента'] == sort_id)]
                dq=b[['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок']]
                dq=dq.drop_duplicates()
                dq.to_csv(trail+'/Сводная_по_водителю1.csv',index=False)
                with open(trail+'/Сводная_по_водителю1.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    data1 = list(zip(*rows)) 
                dw=b[['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']]
                dw=dw.drop_duplicates()
                dw.to_csv(trail+'/Сводная_по_водителю2.csv',index=False)
                with open(trail+'/Сводная_по_водителю2.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    data2 = list(zip(*rows))           
                r = csv.reader(open(trail+'/Сводная_по_водителю1.csv'))
                lines = list(r)
                cid=lines[1][1] 
                b=df.loc[ (df['ИД клиента'] == cid)]
                test=['Дуэт','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']
                de=b[test]
                de=de.sort_values(['Дуэт'], ascending=[False])
                de=de.drop_duplicates()
                de.to_csv(trail+'/Сводная_по_водителю3.csv',index=False, header=False)
                with open(trail+'/Сводная_по_водителю3.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    dee = list(rows)                 
                return render(request,'check/Driver.html' , {"data1":data1,
                                                                    "data2":data2,
                                                                    "de":de,
                                                                    "dee":dee}) 
        else:

            dw=df[['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']]
            dw=dw.drop_duplicates()
            dw.to_csv(trail+'/Сводная_по_водителю2.csv',index=False)
            with open(trail+'/Сводная_по_водителю2.csv') as csvfile:
                rows = csv.reader(csvfile)
                data2 = list(zip(*rows))                      
            test=['Имя клиента','ИД клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']
            de=df[test]
            de=de.sort_values(['Дуэт'], ascending=[False])
            de=de.drop_duplicates()
            de.to_csv(trail+'/Сводная_по_водителю3.csv',index=False, header=False)
            with open(trail+'/Сводная_по_водителю3.csv') as csvfile:
                rows = csv.reader(csvfile)
                dee = list(rows)         
            return render(request,'check/Driver.html' ,{"data2":data2,
                                                                "de":de,
                                                                "dee":dee})
    except:
        trip_id = request.POST['sort_id']
        driver_id,customer_id,drv_id=sqlvertica.sql_trip(trip_id)
        sqlvertica.sql_old_drv(drv_id,trail)
        return redirect("/check/Driver/1/")                                                          



class svod_doplat(LoginRequiredMixin, View):
    def get(self,request):
        start_date=(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')
        end_date=datetime.now().strftime('%Y-%m-%d')
        return render(request,'check/svod_dop.html',{"start_date":start_date
                                                    ,"end_date":end_date})
    def post(self,request):
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        сity=City.objects.all()
        head,data=sqlvertica.sql_doplat(start_date,end_date) 
  
        return render(request,'check/svod_dop.html',{"start_date":start_date
                                                    ,"end_date":end_date
                                                    ,"head":head
                                                    ,"сity":сity
                                                    ,"data":data})





class rez_prover(LoginRequiredMixin, View):
    def get(self,request):
        сity=City.objects.all() 
        return render(request,'check/rez_prov.html',{"сity":сity
                                                    })


class brend(LoginRequiredMixin, View):
    def get(self,request):                                                    
        return render(request,'check/brend.html')
    def post(self,request):
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]  
        driver_id = request.POST["driver_id"] 
        dr_dl=len(driver_id)
        if dr_dl > 9:
            driver_id=sqlvertica.sql_drv_id(driver_id)[0][0]
        head,data=sqlvertica.sql_drv_poezd(driver_id,start_date,end_date)
        return render(request,'check/brend.html',{"start_date":start_date
                                                    ,"end_date":end_date
                                                    ,"drv_id":driver_id
                                                    ,"head":head
                                                    ,"data":data

                                                     })  
                                                  
def dash(request,**kwargs):
    trail="check/templates/csv"+request.user.username
    return HttpResponse(dispatcher(request,trail))
@csrf_exempt      
def dash_ajax(request):
    trail="check/templates/csv"+request.user.username 
    return HttpResponse(dispatcher(request,trail),content_type='application/json')  


