from django.views.decorators.csrf import csrf_exempt, csrf_protect,requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,render_to_response,redirect
from django.template import loader, Context
from django.http import HttpResponse
from django.contrib import auth
from django.views import View
from django.views.generic import TemplateView

from .models import FraudOrders,google_sheet,option_city
from  django.apps  import apps
from .import_data import update_db_fraud_orders ,order_id_zar
from check import sqlvertica 
from .track_points_map import get_info_from_bo as gifb
from .main import Update
from .loading_trips import trips_affecting_the_bonus_plan ,trips_with_surcharges

import pandas as pd
import os
from datetime import datetime,timedelta
import sys



def filter_dan(gorod,start_time,end_time):
    end_time=(datetime.strptime(end_time,'%Y-%m-%d')+ timedelta(days=1)).strftime('%Y-%m-%d')
    if gorod=='ALL' :
        FraudOrder=FraudOrders.objects.filter(order_date__range=(start_time,end_time))
    elif gorod=='0':
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
def resol_count(resol,FraudOrder):
        resol_N=[]
        for i in resol:
            resol_N.append(FraudOrder.filter(resolution=i).count())
        return resol_N
class Fraud_inspector(LoginRequiredMixin, View):
    def get(self,request):
        end_time= datetime.now().strftime('%Y-%m-%d')
        start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        City=check_city()
        gorod="ALL"
        FraudOrder=filter_dan(gorod,start_time,end_time)
        resol=["UNVERIFIED" ,"FRAUD YES","FRAUD NO"]
        resol_N= resol_count(resol,FraudOrder) 
        return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                                        "end_time":end_time,
                                                                        "resol_N":resol_N,
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
            resol_N= resol_count(resol,FraudOrder) 
            return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                            "resol":resol,
                                                            "resol_N":resol_N,
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
            resol_N= resol_count(resol,FraudOrder) 
            return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                            "gorod":gorod,
                                                            "resol_N":resol_N,
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
        resol_N= resol_count(resol,FraudOrder) 
        return render (request,'fraud_inspector/Fraud_inspector.html',{"City":City,
                                                "gorod":gorod,
                                                "resol_N":resol_N,
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
    del cus_head
    del drv_hed
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
                                                           # "track_points":track_points,
                                                            "FraudOrder":FraudOrder

        })
@csrf_exempt
def option_city_trips(gorod, start_time,end_time):
        city_all=[]
        if gorod == "0":
            all_city=option_city.objects.values_list()
            for i in all_city:
                i=list(i)
                if i[2] != 0:
                    city_all.append(i[2])
        else:
            city_gor=option_city.objects.filter(launch_region_id=gorod).values_list()
            gorod=(list(city_gor[0]))
            city_all.append(gorod[2])  
        for city_id in city_all: 
            j_slov=option_city.objects.filter(launch_region_id=city_id).values().first() 
            if j_slov['loading_trips_with_surcharges'] !=0:
                trips_with_surcharges (start_time,end_time,city_id)
            if j_slov['loading_trips_affecting_the_bonus_plan']!=0:  
                city_bonus_plan_dict=City_table_bonus_plan_dict(city_id)
                trips_affecting_the_bonus_plan (city_id,start_time,end_time,city_bonus_plan_dict)
            if j_slov['loading_trips_trips_without_surcharges']!=0:
                update_db_fraud_orders(city_id,start_time,end_time)      
        return 

class zagr_tr(LoginRequiredMixin, View):
    def get(self,request):
        end_time  = datetime.now().strftime('%Y-%m-%d')
        start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        City=option_city.objects.all()
        gorod=0
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
            option_city_trips(gorod,start_time,end_time)
            City=option_city.objects.all()
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
            City=option_city.objects.all()
            gorod=0
            blocked_unblocked(trip_id,'UNBLOCKED')
            msg="Заказ разблокирован:"+trip_id
            return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                    "gorod":gorod,
                                                                    "end_time":end_time,
                                                                    "start_time":start_time,
                                                                    "msg":msg


    })
        elif function=="p_3":
            order_id= request.POST["order_id"]
            end_time  = datetime.now().strftime('%Y-%m-%d')
            start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
            City=option_city.objects.all()
            gorod=0
            order_id_zar(order_id)
            msg_2="Заказ добавлен:"+order_id
            return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                    "gorod":gorod,
                                                                    "end_time":end_time,
                                                                    "start_time":start_time,
                                                                    "msg_2":msg_2


    })
        elif function=="Выполнить":
            end_time  = datetime.now().strftime('%Y-%m-%d')
            start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
            City=option_city.objects.all()
            gorod=0
            FraudOrders.objects.filter(state='BLOCKED').update(state='UNBLOCKED')
            msg_3="Заказы разблокированы"
            return render(request,'fraud_inspector/zagr_sbros.html',{"City":City,
                                                                    "gorod":gorod,
                                                                    "end_time":end_time,
                                                                    "start_time":start_time,
                                                                    "msg_3":msg_3


    })

def City_google():
    City_t=google_sheet.objects.values_list()
    City=[]
    for i in City_t: 
        i=list(i) 
        City.append([str(i[1]),str(i[2]),str(i[3])])
    City=pd.DataFrame(City)
    City = City.drop_duplicates()
    City = City.values.tolist() 
    
    return City

def City_table_bonus_plan_dict(region_id):
    City_t=google_sheet.objects.filter(launch_region_id=region_id)
    City_t=City_t.values_list()
    city_bonus_plan_dict=[]
    for i in City_t: 
        i=list(i) 
        city_bonus_plan_dict.append([i[4],i[5],i[6]])
    return city_bonus_plan_dict

class google__Sheet(LoginRequiredMixin, View):
    def get (self,request):

        week=datetime.now().isocalendar()[1]
        now = datetime.now().strftime('%Y')
        now = now + '-W'+str(week)
        City=City_google()
        return render( request,'fraud_inspector/google_Sheet.html',{"City":City,
                                                                    "now":now
        })
    def post (self,request):
        gorod= request.POST["kod_city"]
        time_week= request.POST["time_week"]
        City=google_sheet.objects.all()
        year,week=time_week.split("-W")
        City=City_google()
        city_bonus_plan_dict=City_table_bonus_plan_dict(gorod) 
        Update(week, year, gorod,city_bonus_plan_dict,City) 
        msg="Заказ загружен  :"+week+"   "+year
        return render( request,'fraud_inspector/google_Sheet.html',{"City":City,
                                                                    "gorod":gorod,
                                                                    "msg":msg,
                                                                    "now":time_week,
                                                                    
        })


class test_map(LoginRequiredMixin,TemplateView):
    def get(self,request):
      #  order='0701ea4c-c7bb-4207-ac5f-a39b73e0fd6b'
       # order_details= gifb('HTTP received https://manager-http-gtw.k.fasten.com/history/api/public/v1/manager/orders/0701ea4c-c7bb-4207-ac5f-a39b73e0fd6b','{"order_id": "0701ea4c-c7bb-4207-ac5f-a39b73e0fd6b"}')
        order_details= gifb('MANAGER_GET_ORDER_DETAILS', '{"order_id": "aaeb2171-cb22-4e05-ad0e-726b5614947c"}')
        for key, val in order_details.items():
            if key == 'order_details':
                for i, j in val.items(): 
                    if i == 'track_points':
                        order_points=j
        order_points=order_points.split(';')
        order_points=list(([x] for x in order_points))[:-1]
        track_points=[]
        for ch in order_points:                                                                                                     
            for i in ch:
                    q,w=i.split(',')
                    i=float(w),float(q)
                    i=list(i)
                    track_points.append(i)
        
        return render( request,'fraud_inspector/test_map.html',{"track_points":track_points})
    
def order_id_points(order_id):
    order_details= gifb('MANAGER_GET_ORDER_DETAILS','{"order_id": "'+order_id+'"}')
    for key, val in order_details.items():
        if key == 'order_details':
            for i, j in val.items(): 
                if i == 'track_points':
                    order_points=j
    order_points=order_points.split(';')
    order_points=list(([x] for x in order_points))[:-1]
    track_points=[]
    for ch in order_points:                                                                                                     
        for i in ch:
                q,w=i.split(',')
                i=float(w),float(q)
                i=list(i)
                track_points.append(i)
    return track_points
     
class test_123 (LoginRequiredMixin, View):
    def get (self,request):
        page_size=10
        df=pd.read_csv('/home/vkondratev/anti_fraud/check/templates/csvvkondratev/Сводная_по_водителю.csv')
        df['N'] = range(1, len(df) + 1)
        _list=df['N'].count()
        df=df[df['N']>=1]
        df=df[df['N']<=10] 
        head=df.columns.tolist()
        data=df.values.tolist()
        stranic=str(float(_list)/float(page_size))
        stran,ost=stranic.split('.')
        if ost!='0':
            kol_stranic=int(stran)+1
        else:
            kol_stranic=int(stran)
        _str=1 
        context={"page_size":page_size,"head":head,"sstr":_str,"data":data,"kol_stranic":kol_stranic,"list":_list}
        return render (request , 'fraud_inspector/test.html',context)                 

    def post (self,request):     
        page_size= int(request.POST["page_size"])
        __list=request.POST["list"] 
        keys=request.POST["key"]
        fil_ter=request.POST["fil_ter"]
        _str=int(request.POST["sstr"])
        df=pd.read_csv('/home/vkondratev/anti_fraud/check/templates/csvvkondratev/Сводная_по_водителю.csv')
        df=df.astype('str')
        if fil_ter.replace(" ", '')!='':
            df=df[(df.values  == fil_ter)]
        df['N'] = range(1, len(df) + 1)    
        key,nkey=keys.split('.')
        if nkey=='n1':
            df=df.sort_values([key], ascending = [1])
        elif nkey=='n2':
            df=df.sort_values([key], ascending = [0])
        else:        
            df=df.sort_values(['N'], ascending = [1])
        head=df.columns.tolist()
        _list=df['N'].count()
        stranic=str(float(_list)/float(page_size))
        stran,ost=stranic.split('.')
        if ost!='0':
            kol_stranic=int(stran)+1
        else:
            kol_stranic=int(stran)  
        if __list == 'start':
            _str=1
        elif __list=="end":
            _str=kol_stranic
        elif __list=='+1':
            _str=_str+1 
            if _str> kol_stranic:
                _str=kol_stranic
               
        elif __list=='-1':
            _str=_str-1 
            if _str == 0:
                _str=1                
        if _str>kol_stranic:
            _str=kol_stranic
        index_max=_str*int(page_size)
        index_min=_str*int(page_size)-int(page_size)+1     
        df=df[df['N']>=index_min]
        df=df[df['N']<=index_max]
        data=df.values.tolist() 
        context ={"page_size":page_size,"head":head,"fil_ter":fil_ter,"sstr":_str,"nkey":nkey,"key":key,"data":data,"kol_stranic":kol_stranic,"list":_list}
        return render (request , 'fraud_inspector/test.html',context)         

class city_option(LoginRequiredMixin, View):
    def get (self,request):

        city=option_city.objects.all()
        context={"city":city}
        return render (request,'fraud_inspector/city_option.html',context)
    def post (self,request):
        groups = request.user.groups.values_list()#'Группа_1', flat=True
        for group in groups:
            if group[1] == 'Группа_1':   
                try:
                    filt=request.POST["filter"] 
                    if filt=='':
                        city=option_city.objects.all()
                    else:    
                        city=option_city.objects.filter(city__contains= filt)
                    context={"city":city}
                    return render (request,'fraud_inspector/city_option.html',context)
                except:
                    city=option_city.objects.values_list()
                    for i in city:
                        if i[1] !='Все города':
                            loading_trips_with_surcharges=request.POST[str(i[2])+'.loading_trips_with_surcharges']
                            loading_trips_affecting_the_bonus_plan=request.POST[str(i[2])+'.loading_trips_affecting_the_bonus_plan']
                            loading_trips_trips_without_surcharges=request.POST[str(i[2])+'.loading_trips_trips_without_surcharges']
                            option_city.objects.filter(city=i[1]).update(loading_trips_with_surcharges=loading_trips_with_surcharges,
                            loading_trips_affecting_the_bonus_plan=loading_trips_affecting_the_bonus_plan,loading_trips_trips_without_surcharges=loading_trips_trips_without_surcharges)
        city=option_city.objects.all()
        context={"city":city}
        return render (request,'fraud_inspector/city_option.html',context)     


class prov_dop(LoginRequiredMixin, View):
    def get(self,request):
        doplat=google_sheet.objects.all()
        context={"doplat":doplat}
        return render (request,'fraud_inspector/doplat_option.html',context)


class peremen_fraud_ins():
    _list=["list1","list2","list3"]
    zap=["zap1","zap2","zap3"]
    _str=["sstr1","sstr2","sstr3"]
    resol=["UNVERIFIED" ,"FRAUD YES","FRAUD NO"]
    resol_name=[["UNVERIFIED","НЕ ПРОВЕРЕНО"],["FRAUD YES","ФРОД"],["FRAUD NO","НЕ ФРОД"]]
    data=["data1","data2","data3"]
    kol_stranic=["kol_stranic1","kol_stranic2","kol_stranic3"]
    
    head=['N','order_id','order_date','launch_region_id','driver_id','pattern_name','compensation','state']

def fraud_inspector_sc(dff,page_size,_str,_list,key,sor_t):
    for i in range(len(peremen_fraud_ins.resol)):
            df=dff[(dff['resolution']==  peremen_fraud_ins.resol[i])]
            df['N']=range(1,len(df)+1)
            peremen_fraud_ins.zap[i]=df['N'].count()
            df=df[peremen_fraud_ins.head]
            try:
                df[key]=df[key].astype('int')
            except:
                pass
            df=df.sort_values([key], ascending = [sor_t])
            df['order_date']=df['order_date'].astype('datetime64[ns]')   
            stranic=str(float(peremen_fraud_ins.zap[i])/float(page_size))
            stran,ost=stranic.split('.')
            if ost != '0':
                peremen_fraud_ins.kol_stranic[i]=int(stran)+1
            elif stran == '0':
                peremen_fraud_ins.kol_stranic[i]=1
            else:
                peremen_fraud_ins.kol_stranic[i]=int(stran)
            if _list[i] == 'start':
                _str[i]=1
            elif _list[i]=="end":
                _str[i]=peremen_fraud_ins.kol_stranic[i]
            elif _list[i]=='+1':
                _str[i]=_str[i]+1 
                if _str[i]> peremen_fraud_ins.kol_stranic[i]:
                    _str[i]=peremen_fraud_ins.kol_stranic[i]
            elif _list[i]=='-1':
                _str[i]=_str[i]-1 
                if _str[i] == 0:
                    _str[i]=1

            if _str[i]>peremen_fraud_ins.kol_stranic[i]:
                _str[i]=peremen_fraud_ins.kol_stranic[i] 
            
        
            index_max=int(_str[i])*int(page_size)
            index_min=int(_str[i])*int(page_size)-int(page_size)+1  
            df['N']=range(1,len(df)+1)   
            df=df[df['N']>=index_min]
            df=df[df['N']<=index_max]
            peremen_fraud_ins.data[i]=df.values.tolist()
    return peremen_fraud_ins.data ,peremen_fraud_ins.kol_stranic,peremen_fraud_ins.zap

def fraud_inspector_head():
    head=[]
    for e in FraudOrders._meta.get_fields():
        head.append((str(e)).replace("fraud_inspector.FraudOrders.", ''))
    return head
def sort_df(data,key,sor_t):
    dff=pd.DataFrame(data,columns=peremen_fraud_ins.head)
    try:
       dff[key]=dff[key].astype('int')
    except:
        pass
    dff=dff.sort_values([key], ascending = [sor_t])
    dff['order_date']=dff['order_date'].astype('datetime64[ns]') #datetime64
    data=dff.values.tolist()
    return  data



def dff_fil(dff,fil__ter,fil_ter,cont):
    dff=dff.loc[(dff[fil__ter] == fil_ter)]
    zap_cont(cont,"fil__ter",fil__ter)
    zap_cont(cont,"fil_ter",fil_ter)
    return dff,cont
def zap_cont(cont,per_1,per_2):
    cont.append(per_1)
    cont.append(per_2)
class fraud_inspector_ver_2(LoginRequiredMixin, View):
    def get(self,request):
        gorod='0'
        page_size=10
        end_time= datetime.now().strftime('%Y-%m-%d')
        start_time= (datetime.now()- timedelta(days=1)).strftime('%Y-%m-%d')
        head=fraud_inspector_head()
        FraudOrder=filter_dan(gorod,start_time,end_time)
        FraudOrder_=FraudOrder.values_list()
        dff=pd.DataFrame(FraudOrder_,columns=head)
        _str=[1,1,1] 
        _list=[1,1,1]
        data,kol_stranic,zap=fraud_inspector_sc(dff,page_size,_str,_list,"N",1)
        city=option_city.objects.all()
        fil_ter=""
        context={"City":city,"gorod":gorod,"end_time":end_time,"start_time":start_time,"resol_name":peremen_fraud_ins.resol_name,
        "head":peremen_fraud_ins.head,"inset_":"tab_2","fil_ter":fil_ter,
        "data":data,"kol_stranic":kol_stranic,"zap":zap,"page_size":page_size,"sstr":_str}
        return render (request,'fraud_inspector/Fraud_inspector_test.html',context)

    def post(self,request):
        cont=[]
        try:
            save=request.POST["save"]
            resolution= request.POST["resolution"]
            blocked_unblocked(save,'UNBLOCKED')
            FraudOrders.objects.filter(order_id=save).update(resolution=resolution)
        except:
            pass
        try:
            save=request.POST["save_1"]
            blocked_unblocked(save,'UNBLOCKED')
        except:
            pass    
        gorod=request.POST["gorod"]
        end_time=request.POST["end_time"]
        start_time=request.POST["start_time"]
        page_size=request.POST["page_size"]
        inset=request.POST["inset"]
        if inset=='':
            inset='tab_1'
        head=fraud_inspector_head()
        FraudOrder=filter_dan(gorod,start_time,end_time)
        _str=[]
        for i in range(0,len(peremen_fraud_ins._str)):
            _str.append(int(request.POST[peremen_fraud_ins._str[i]]))
        _list=[]
        for i in range(0,len(peremen_fraud_ins._list)):
            try:
                _list.append(request.POST[peremen_fraud_ins._list[i]])
            except:
                _list.append(1) 
        try:
            fil_ter=request.POST["fil_ter"]
            fil__ter=request.POST["fil__ter"]
            FraudOrder_=FraudOrder.values_list()
            dff=pd.DataFrame(FraudOrder_,columns=head)
            if fil_ter.replace(" ", '')!='':
#                dff=dff[(dff.values  == fil_ter)]
                dff,cont=dff_fil(dff,fil__ter,fil_ter,cont)
        except:
            FraudOrder_=FraudOrder.values_list()
            dff=pd.DataFrame(FraudOrder_,columns=head)
               
        page_size=request.POST["page_size"]
        try:
            keys=request.POST["key"]
            key,nkey=keys.split('.')
        except:
            key="N"   
            nkey="n0"
        zap_cont(cont,"key",key)
        zap_cont(cont,"nkey",nkey)
        if nkey=='n1':
            key,sort=key,1
        elif nkey=='n2':
            key,sort=key, 0
        else:        
            key,sort="N",1    
        data,kol_stranic,zap=fraud_inspector_sc(dff,page_size,_str,_list,key,sort)
        city=option_city.objects.all() 



        try:
            block=request.POST["block"]
            state_zak=FraudOrders.objects.values_list('state', flat=True).filter(order_id=block)
            state="BLOCKED"
            if str(state_zak[0])==state:
                msg="Заказ № "+block+" проверяет другой пользователь"
                zap_cont(cont,"msg",msg)
            else:
                blocked_unblocked(block,state)
                pattern=FraudOrders.objects.values_list('pattern_name', flat=True).filter(order_id=block)
                pattern=pattern[0].split(",")
                FraudOrder=FraudOrders.objects.filter(order_id=block)
                driver_id,customer_id,drv_id=sqlvertica.sql_trip(block)
                chek_box='yes'
                cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus, time =\
                    sqlvertica.sql_prov(customer_id, driver_id, drv_id, chek_box)
                del cus_head
                del drv_hed
                PRV="1"
                zap_cont(cont,"order_id_zac",block)
                zap_cont(cont,"pattern",pattern)
                zap_cont(cont,"cus",cus)
                zap_cont(cont,"PRV",PRV)
                zap_cont(cont,"drv",drv)
                zap_cont(cont,"svod_drv_cus_head",svod_drv_cus_head)
                zap_cont(cont,"svod_drv_cus",svod_drv_cus)
                zap_cont(cont,"svod_cus_head",svod_cus_head)
                zap_cont(cont,"svod_cus",svod_cus)
                zap_cont(cont,"time",time)
                zap_cont(cont,"FraudOrder",FraudOrder)
        except:
            pass
    
        aa=["City",city,"gorod",gorod,"end_time",end_time,"start_time",start_time,"resol_name",peremen_fraud_ins.resol_name,
        "head",peremen_fraud_ins.head,"inset_",inset,"resol",peremen_fraud_ins.resol,
        "data",data,"kol_stranic",kol_stranic,"zap",zap,"page_size",page_size,"sstr",_str]
        for i in aa:
            cont.append(i)
        context = {}
        for i in range(0, len(cont)-1, 2):
            context[cont[i]] = cont[i+1]
        return render (request,'fraud_inspector/Fraud_inspector_test.html',context)



class test_qwe (LoginRequiredMixin, View):
    def get(self,request):
        context={"msg":"qwe"}
        return render (request,'fraud_inspector/test1.html',context)    
    def post(self,request):
        context={"msg":"qwe"}
        return render (request,'fraud_inspector/test1.html',context)        