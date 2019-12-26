from datetime import datetime,timedelta
import time
from .models import FraudOrders,google_sheet,option_city
from .loading_trips import trips_affecting_the_bonus_plan ,trips_with_surcharges
from .import_data import update_db_fraud_orders

def auto_update():
    while 1:
        print("!")
        all_city=option_city.objects.values_list()
        end_time,start_time= (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),(datetime.now()- timedelta(days=2)).strftime('%Y-%m-%d')
        all_city=option_city.objects.values_list()
        city_all=[]
        for i in all_city:
            i=list(i)
            if i[2] != 0:
                    city_all.append(i[2])
        for city_id in city_all: 
            j_slov=option_city.objects.filter(launch_region_id=city_id).values().first() ####!!!
            if str(j_slov['loading_trips_with_surcharges']) !='0' :
                trips_with_surcharges(start_time,end_time,city_id)
            if str(j_slov['loading_trips_affecting_the_bonus_plan'])!='0':  
                City_t=google_sheet.objects.filter(launch_region_id=city_id)
                City_t=City_t.values_list()
                city_bonus_plan_dict=[]
                for i in City_t: 
                    i=list(i) 
                    city_bonus_plan_dict.append([i[4],i[5],i[6]])  
                trips_affecting_the_bonus_plan(city_id,start_time,end_time,city_bonus_plan_dict)
            if str(j_slov['loading_trips_trips_without_surcharges'])!='0':
                update_db_fraud_orders(city_id,start_time,end_time)      
        time.sleep(3600*3)
 