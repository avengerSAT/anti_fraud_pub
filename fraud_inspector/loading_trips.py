from datetime import datetime as dt , timedelta 
import datetime  
import pandas as pd 
from isoweek import Week
from vertica_python import connect
from .con import Con_vert
from contextlib import closing
from fraud_inspector.models import FraudOrders
import csv
from csv import writer

def update_db_fraud_orders(data):
    for row in data:
        try:
            now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            post = FraudOrders()
            post.order_id = row[0]
            post.order_date = row[1]
            post.launch_region_id = row[2]
            post.driver_id = row[3]
            post.customer_id = row[4]
            post.state = row[5]
            post.pattern_name = row[6]
            post.resolution = row[7]
            post.compensation = row[8]
            post.save()
            row.append(now)
            with open("templates/logs.csv", "a", newline='') as csv_file:
                csv_writer = writer(csv_file, delimiter=',')
                csv_writer.writerow(row)
        except:
            pass            
    return 

def trips_with_surcharges (date_from, date_to, city_id):
    city_id=str(city_id)
    date_from, date_to=date_from.replace("-", ''), date_to.replace("-", '')
    with closing(connect(host=Con_vert.host,
                                    port=Con_vert.port,
                                    user=Con_vert.user,
                                    password=Con_vert.password,
                                    data_base=Con_vert.data_base,
                                    read_timeout=Con_vert.read_timeout)
                            ) as con:
        with open('./fraud_inspector/Sql/treck_dop.sql', 'r') as sql:
            data = pd.read_sql_query(sql.read(), con, params=[date_from, date_to, city_id])
            
            data=data[['order_id','order_date','launch_region_id','driver_id','customer_id','pattern_name','state','resolution','compensation']] 
            data = data.drop_duplicates() 
            test = (data.groupby(['order_id'])['pattern_name']
                        .apply(', '.join).reset_index(name='pattern_name'))
            del data['pattern_name'] 
            data = data.drop_duplicates()  
            data = pd.merge(data, test, on='order_id')
            data = data.fillna(0)
            columns = data.columns.tolist()
            columns = columns[:6] + columns[-1:] + columns[6:-1]
            data = data[columns]
            data[['driver_id', 'compensation']] = \
            data[['driver_id', 'compensation']].astype(int).astype(str)
            data = data.drop_duplicates()
            data = data.values.tolist()
    update_db_fraud_orders(data)
    return            

def TotalFraudTable_ned(date_from, date_to, city_id, week, year, min_trips_for_bonus,city_bonus_plan_dict):
    try:
        with closing(connect(host=Con_vert.host,
                            port=Con_vert.port,
                            user=Con_vert.user,
                            password=Con_vert.password,
                            data_base=Con_vert.data_base,
                            read_timeout=Con_vert.read_timeout)
                    ) as con:


            with open('./fraud_inspector/Sql/TotalFraudTable.sql', 'r') as sql:
                df = pd.read_sql_query(sql.read(), con, params=[date_from, date_to, city_id, week, year, min_trips_for_bonus])
            df.loc[df['Успешных поездок'] >= city_bonus_plan_dict[0][0], 'Получен бонус план'] = city_bonus_plan_dict[0][1]
            for i in city_bonus_plan_dict:
                df.loc[df['Успешных поездок'] < i[0],
                    'Получен бонус план'] = i[2]

            df.loc[df['Успешных за вычетом фродовых'] >=
                city_bonus_plan_dict[0][0], 'К списанию'] = 0
            for i in city_bonus_plan_dict:
                df.loc[df['Успешных за вычетом фродовых'] < i[0],'К списанию'] = df['Получен бонус план'] - i[2]
            total_fraud_table = df.drop_duplicates(subset=['Длинный позывной', 'Короткий позывной'], keep='first')
        total_fraud_table=total_fraud_table.values.tolist()
        drv_ids = []
        for i in total_fraud_table:
            if i[8] != 0:
                if i[1] != 0:
                    drv_ids.append(str(i[1]))
        drv_ids = tuple(drv_ids)
        with closing(connect(host=Con_vert.host,
                                port=Con_vert.port,
                                user=Con_vert.user,
                                password=Con_vert.password,
                                data_base=Con_vert.data_base,
                                read_timeout=Con_vert.read_timeout)
                        ) as con:

            
            with open('./fraud_inspector/Sql/zagr_treck_dop.sql', 'r') as sql:
                data = pd.read_sql_query(sql.read(), con, params=[date_from, date_to, city_id, drv_ids]) 
                
                test = (data.groupby(['order_id'])['pattern_name']
                            .apply(', '.join).reset_index(name='pattern_name'))
                del data['pattern_name']
                data = pd.merge(data, test, on='order_id')
                data = data.fillna(0)
                columns = data.columns.tolist()
                columns = columns[:6] + columns[-1:] + columns[6:-1]
                data = data[columns]
                data[['driver_id', 'compensation']] = \
                data[['driver_id', 'compensation']].astype(int).astype(str)
                data = data.drop_duplicates()
                data = data.values.tolist()
                
        update_db_fraud_orders(data)            
        return 
    except:
        return



def trips_affecting_the_bonus_plan (city_id,date_start,date_end,city_bonus_plan_dict):
    date_format = "%Y-%m-%d"
    city_id=str(city_id)
    nedels=[]
    a = dt.strptime(date_start, date_format)
    b = dt.strptime(date_end, date_format)
    delta = b - a

    for i in range(delta.days+1):
        year, month, day=((dt.strptime(date_start, date_format)+ timedelta(days=i)).strftime(date_format)).split('-')
        nedel=datetime.date(int(year), int(month), int(day)).isocalendar()[1]
        if [year,nedel] not in  nedels:
            nedels.append([year,nedel])
    for i in nedels:
        year=i[0]
        week=i[1]
        date_from, date_to = (Week(int(year), int(week)).monday().strftime('%Y%m%d')),(Week(int(year),int(week+1)).monday().strftime('%Y%m%d'))
        min_trips_for_bonus = city_bonus_plan_dict[-1][0]
        TotalFraudTable_ned(date_from, date_to, city_id, week, year, min_trips_for_bonus,city_bonus_plan_dict)

    return 


