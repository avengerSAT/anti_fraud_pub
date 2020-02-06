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
from django.apps  import apps
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response
from django.template import Context, loader
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count

import threading
from datetime import datetime,timedelta
from django.views.decorators.csrf import (csrf_exempt, csrf_protect,
                                          requires_csrf_token)
from isoweek import Week

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from  django.apps  import apps
from . import import_bd, import_csv, sqlvertica
from .models import City
from .templates.dash_.dash_1 import dispatcher 




def fraud_inspector_FraudOrders():
    FraudOrders=apps.get_model('fraud_inspector','FraudOrders')
    FraudOrders=FraudOrders.objects.all()
    return FraudOrders

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
            cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus, time =\
                sqlvertica.sql_prov(customer_id, driver_id, drv_id, chek_box)
            chek_box='checked'
        else:
            cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus, time =\
                sqlvertica.sql_prov(customer_id, driver_id, drv_id, chek_box)
            chek_box=''
        
        return render (request,'check/test_prover.HTML',{"cus":cus,
                                                    "drv":drv,
                                                    "trip_id":trip_id,
                                                    "box_c":chek_box,
                                                    "svod_drv_cus_head":svod_drv_cus_head,
                                                    "svod_drv_cus":svod_drv_cus,
                                                    "svod_cus_head":svod_cus_head,
                                                    "svod_cus":svod_cus,
                                                    "time":time})     

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
        df['Статус']=df['Статус']+" / "+df['Статус р'] 
        if request.method == 'POST':
            sort_id = request.POST['sort_id']
            if sort_id =="":
                dw=df[['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']]
                dw=dw.drop_duplicates()
                dw.to_csv(trail+'/Сводная_по_водителю2.csv',index=False)
                with open(trail+'/Сводная_по_водителю2.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    data2 = list(zip(*rows))        
                test=['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Статус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']                    
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
                dq=b[['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Статус','Кол поездок клиента','Дуэт','Доля совместных поездок']]
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
            test=['Имя клиента','ИД клиента','Статус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']
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
        brend = "fasten"                                             
        return render(request,'check/brend_1.html',{"brend":brend
                                                    })
    def post(self,request):
        brend=request.POST["brend_1"] 
        try:
            if brend == 'fasten':
                start_date = request.POST["start_date"]
                end_date = request.POST["end_date"]  
                driver_id = request.POST["driver_id"] 
                dr_dl=len(driver_id)
                if dr_dl > 9:
                    driver_id=sqlvertica.sql_drv_id(driver_id)
                FraudOrders=fraud_inspector_FraudOrders()
                Count=FraudOrders.filter(driver_id=driver_id,order_date__range=(start_date,end_date),resolution='FRAUD YES') 
                Count=Count.count() 
                head,data=sqlvertica.sql_drv_poezd(driver_id,start_date,end_date)
                try:
                    if data[0][1] is None :
                        data[0][1]=0
                        data[0][2]=data[0][0]
                    data[0][1]=int(data[0][1])+int(Count)
                    data[0][2]=int(data[0][2])-int(Count)
                except:
                    data=[[0,0,0]]  
                with open('check/lime_city.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    City = list(rows)      
                return render(request,'check/brend_1.html',{"start_date":start_date
                                                            ,"brend":brend
                                                            ,"City":City
                                                            ,"end_date":end_date
                                                            ,"drv_id":driver_id
                                                            ,"head":head
                                                            ,"data":data
                                                            })  

            else:
                with open('check/lime_city.csv') as csvfile:
                    rows = csv.reader(csvfile)
                    City = list(rows) 
                start_date = request.POST["start_date_1"]
                end_date = request.POST["end_date_1"]  
                driver_id = request.POST["driver_id_1"] 
                city = request.POST["city"] 
                start_date_1=start_date.replace("-", '')
                end_date_1=int(end_date.replace("-", ''))+1
                head,data=sqlvertica.sql_LM_brend(city,driver_id,start_date_1,end_date_1) 
                return render(request,'check/brend_1.html',{"start_date_1":start_date
                                            ,"brend":brend
                                            ,"city":city
                                            ,"City":City
                                            ,"end_date_1":end_date
                                            ,"driver_id_1":driver_id
                                            ,"head_1":head
                                            ,"data_1":data
                                            })                                               
        except:
            try: 
                city = request.POST["city"] 
            except:
                pass     
            with open('check/lime_city.csv') as csvfile:
                rows = csv.reader(csvfile)
                City = list(rows)             
            msg="Проверьте правильность вводимых данных"                                             
            return render(request,'check/brend_1.html',{"msg":msg
                                                        ,"city":city
                                                        ,"City":City
                                                        })           
            
                                   
def dash(request,**kwargs):
    trail="check/templates/csv"+request.user.username
    return HttpResponse(dispatcher(request,trail))
@csrf_exempt      
def dash_ajax(request):
    trail="check/templates/csv"+request.user.username 
    return HttpResponse(dispatcher(request,trail),content_type='application/json')  


class otchet_kursk(LoginRequiredMixin, View):
    def get (self,request):
        week=datetime.now().isocalendar()[1]
        now = datetime.now().strftime('%Y')
        now = now + '-W'+str(week)
        return render(request,'check/kursk.html',{"now":now}) 
    def post (self,request):  
        time_week= request.POST["time_week"]
        year,week=time_week.split("-W")
        start_date,end_date = Week(int(year), int(week)).monday().strftime('%Y-%m-%d'),Week(int(year),int(week)+1).monday().strftime('%Y-%m-%d')
        FraudOrders=apps.get_model('fraud_inspector','FraudOrders')
        FraudOrder=FraudOrders.objects.filter(launch_region_id=4712,order_date__range=(start_date,end_date)).values_list()
        head=[]
        for e in FraudOrders._meta.get_fields():
            head.append((str(e)).replace("fraud_inspector.FraudOrders.", ''))
        
        
        FraudOrder=pd.DataFrame(FraudOrder,columns=head)
        FraudOrder=FraudOrder[['order_id','resolution']]
        orders=FraudOrder.values.tolist()
        orders_id=[]
        for order in orders:
            orders_id.append(order[0])
        orders_id=tuple(orders_id)
        data=sqlvertica.sql_kursk(orders_id,start_date, end_date)
        FraudOrder = pd.merge(data, FraudOrder,how='left', on='order_id')
        otchet=FraudOrder[['driver_id','d_driver_id','count_orders']]
        otchet=otchet.drop_duplicates() 
        df=FraudOrder[['driver_id','comp']]
        dff = df.groupby(['driver_id']).size().reset_index(name='count')
        df=df.groupby(['driver_id']).sum()
        df_sp=FraudOrder[['driver_id','spis']]
        df_sp=df_sp.groupby(['driver_id']).sum()
        otchet = pd.merge(otchet, dff,how='left', on='driver_id')
        otchet = pd.merge(otchet, df, on='driver_id')
        otchet = pd.merge(otchet, df_sp, on='driver_id')
        FRAUD_YES=FraudOrder[['driver_id','resolution']]
        FRAUD_YES=FRAUD_YES[(FRAUD_YES['resolution']=='FRAUD YES')]
        FRAUD_YES = FRAUD_YES.groupby(['driver_id']).size().reset_index(name='FRAUD_YES')
        FraudOrder = pd.merge(otchet, FRAUD_YES,how='left', on='driver_id') 
        FraudOrder=FraudOrder.fillna(0)      
        FraudOrder=FraudOrder.values.tolist()
        google_kursk(year,week,FraudOrder)
        head=['Ид водителя короткий','Ид водителя короткий','Общее количество order_completed по водителю','Поездок отобранных на фрод','Размер всех доплат в фрод-заказах','Всего списано по фродовым поездкам','Количество подтвержденных фрод поездок']
        Context={"FraudOrder":FraudOrder,"head":head}
        return render(request,'check/kursk.html',Context)  


def google_kursk(year,week,FraudOrder):
    credentials = 'templates/js/client_secret.json' 
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
    gc = gspread.authorize(credentials)
    wks=gc.open_by_key("1eYS1QbeYS3E_zV3uagBjvIt25xYLWsLbztl8sd9uG5w") 
    date_from, date_to = Week(int(year), int(week)).monday().strftime('%Y%m%d'),Week(int(year),int(week)).sunday().strftime('%Y%m%d')
    name_sheet = date_from[:4] + '.' + date_from[4:6] + '.' + date_from[6:] + ' - ' + date_to[:4] + '.' + date_to[4:6] + '.' + date_to[6:] 
    check_worksheet_name = 0
    for i in wks.worksheets():
        if i.title != name_sheet:
            pass
        else:
            check_worksheet_name = 1

    if check_worksheet_name == 1:
        pass
    else:
        wks.duplicate_sheet(wks.worksheet('шаблон').id,
                            new_sheet_name=name_sheet) 
    wks.values_update(
    name_sheet + '!A4',
    params={
        'valueInputOption': 'USER_ENTERED'
    },
    body={
        'values': FraudOrder
    }
                        )     