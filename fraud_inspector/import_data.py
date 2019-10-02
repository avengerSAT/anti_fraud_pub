import csv
import os
import sys

import pandas as pd
import vertica_python
from vertica_python import connect

from fraud_inspector.models import *

from .con import Con_vert


def load_data(date):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as con:
        with open('./fraud_inspector/Sql/load_data-loaddata.sql', 'r') as load_data_sql:
            data = pd.read_sql_query(
                load_data_sql.read(), con, params=[date])
            data.drop_duplicates()
            data = data.groupby(['order_id',
                      'order_date',
                      'launch_region_id',
                      'driver_id',
                      'customer_id',
                      'state',
                      'resolution',
                      'compensation'])['pattern_name']\
                        .apply(', '.join).reset_index(name='pattern_name')
            columns = data.columns.tolist()
            columns = columns[:6] + columns[-1:] + columns[6:-1]
            data = data[columns]
            data[['driver_id', 'compensation']] = \
            data[['driver_id', 'compensation']].astype(int).astype(str)
            data.drop_duplicates()
            data = data.values.tolist()
    return data


def update_db_fraud_orders():
    data = load_data('2019-09-01')




    for row in data:
        a=FraudOrders.objects.filter(order_id=row[0])
        try:
            if a[0]!=row[0]:
                print(a[0])
        except:
   
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