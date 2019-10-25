import csv
import os
import sys

import pandas as pd
import vertica_python
from vertica_python import connect

from fraud_inspector.models import *

from .con import Con_vert


def load_data(date_from,date_to):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as con:
        with open('./fraud_inspector/Sql/load_data-loaddata.sql', 'r') as load_data_sql:
            data = pd.read_sql_query(
                load_data_sql.read(), con, params=[date_from,date_to])
            test = (data.groupby(['order_id'])['pattern_name']
                        .apply(', '.join).reset_index(name='pattern_name'))
            del data['pattern_name']
            data = pd.merge(data, test, on='order_id', how='inner')
            data = data.fillna(0)
            columns = data.columns.tolist()
            columns = columns[:6] + columns[-1:] + columns[6:-1]
            data = data[columns]
            data[['driver_id', 'compensation']] = \
            data[['driver_id', 'compensation']].astype(int).astype(str)
            data = data.drop_duplicates()
            data = data.values.tolist()
    return data
def load_data_g(gorod,date_from,date_to):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as con:
        with open('./fraud_inspector/Sql/load_data-loaddata_g.sql', 'r') as load_data_sql:
            data = pd.read_sql_query(
                load_data_sql.read(), con, params=[gorod,date_from,date_to])
            test = (data.groupby(['order_id'])['pattern_name']
                        .apply(', '.join).reset_index(name='pattern_name'))
            del data['pattern_name']
            data = pd.merge(data, test, on='order_id', how='inner')
            data = data.fillna(0)
            columns = data.columns.tolist()
            columns = columns[:6] + columns[-1:] + columns[6:-1]
            data = data[columns]
            data[['driver_id', 'compensation']] = \
            data[['driver_id', 'compensation']].astype(int).astype(str)
            data = data.drop_duplicates()
            data = data.values.tolist()
    return data

def update_db_fraud_orders(gorod,date_from,date_to):
    if gorod=="ALL":
        data = load_data(date_from,date_to)
    else:
        data = load_data_g(gorod,date_from,date_to)
        
    for row in data:
        try:
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
        except:
            pass


def order_id_zar(order_id):

    data = load_order_id(order_id)    
    for row in data:
        try: 
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
        except: 
            pass
    

def load_order_id(order_id):
        conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

        with connect(**conn_info) as con:
            with open('./fraud_inspector/Sql/load_order_id.sql', 'r') as load_data_sql:
                data = pd.read_sql_query(
                    load_data_sql.read(), con, params=[order_id])
                data = data.drop_duplicates()
                data = data.values.tolist()
        return data