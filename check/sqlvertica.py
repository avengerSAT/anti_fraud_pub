import csv
import os
from csv import writer

import pandas as pd
import vertica_python
from vertica_python import connect

from .con import Con_vert
from .sql_code import sql_vert


def peremen(data, head):
    a = ([column[0].replace("_", ' ') for column in head])
    b = data
    return a, b


def save_csv(data, head, trail):
    with open(trail, "w", newline='') as csv_file:
        csv_writer = writer(csv_file, delimiter=',')
        csv_writer.writerow(head)
        csv_writer.writerows(data)


def save_csv1(data, trail):
    with open(trail, "w", newline='') as csv_file:
        csv_writer = writer(csv_file, delimiter=',')
        csv_writer.writerows(data)


def sql_trip(trail):
    try:
        with connect(
                host=Con_vert.host,
                port=Con_vert.port,
                user=Con_vert.user,
                password=Con_vert.password) as con:

            with open('./check/Sql/sql_trip.sql', 'r') as sql:
                cursor = con.cursor()
                cursor.execute(sql.read(), (trail,))
                data = cursor.fetchall()

                # переменная водитель
                driver_id = data[0][0]
                # переменная клиент
                customer_id = data[0][1]
                # переменная водитель короткий
                drv_id = data[0][2]

            return driver_id, customer_id, drv_id
    except:
        driver_id, customer_id, drv_id = [i for i in ["Нет данных" for i in range(3)]]
        return driver_id, customer_id, drv_id


def sql_prov(customer_id, driver_id, drv_id, chek_box):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as con:
        with con.cursor() as cur:

            with open('./check/Sql/sql_prov-customer_data.sql', 'r') as customer_data:
                cur.execute(customer_data.read(), (customer_id,))
                data = cur.fetchall()
                head = cur.description
                cus_head, cus = peremen(data, head)
            
            with open('./check/Sql/sql_prov-driver_data.sql', 'r') as driver_data:
                cur.execute(driver_data.read(), (driver_id,))
                data = cur.fetchall()
                head = cur.description
                drv_hed, drv = peremen(data, head)
                
            with open('./check/Sql/sql_prov-customer_trips_total_data.sql', 'r') as customer_trips_total_data:    
                cur.execute(customer_trips_total_data.read(), (customer_id, customer_id))
                data = cur.fetchall()
                head = cur.description
                svod_cus_head, svod_cus = peremen(data, head)
                
                
            if chek_box == 'yes':
                path = './check/Sql/sql_prov-customer_driver_duet_data.sql'
                params = (driver_id, customer_id, drv_id)
            else:
                path = './check/Sql/sql_prov-customer_driver_duet_data_short.sql'
                params = (drv_id, customer_id)
            with open(path, 'r') as customer_driver_duet_data:    
                cur.execute(customer_driver_duet_data.read(), params)
                data = cur.fetchall()
                head = cur.description
                svod_drv_cus_head, svod_drv_cus = peremen(data, head)
    return cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus


def sql_doplat(start_date, end_date):
    conn_info = {'host': Con_vert.host,
                 'port': Con_vert.port,
                 'user': Con_vert.user,
                 'password': Con_vert.password}

    
    with connect(**conn_info) as con:
        with con.cursor() as cur:

            with open('./check/Sql/sql_doplat-sql.sql', 'r') as sql:
                cur.execute(sql.read(), (start_date, end_date))
                data = cur.fetchall()
                head = cur.description
                head, data = peremen(data, head)
    return head, data


def sql_old_drv(drv_id, trail):
    try:
        with connect(
                host=Con_vert.host,
                port=Con_vert.port,
                user=Con_vert.user,
                password=Con_vert.password
            ) as con:

            with con.cursor() as cursor:
                with open('./check/Sql/sql_old_drv-sql.sql', 'r') as sql:
                    cursor.execute(sql.read(), (drv_id, drv_id,))
                    data = cursor.fetchall()
                    head = cursor.description
                    a, b = peremen(data, head)
                    put = trail + '/Сводная_по_водителю.csv'
                    save_csv(b, a, put)
        return
    except:

        put = trail + '/Сводная_по_водителю.csv'
        print("Connection error")

        return


def sql_drv_poezd(driver_id, start_date, end_date):
    try:
        with connect(
                host=Con_vert.host,
                port=Con_vert.port,
                user=Con_vert.user,
                password=Con_vert.password
            ) as con:

            with con.cursor() as cursor:
                with open('./check/Sql/sql_drv_poezd-sql.sql', 'r') as sql:
                    cursor.execute(sql.read(), (driver_id, start_date, end_date,
                                        driver_id, start_date, end_date,))
                    data = cursor.fetchall()
                    head = cursor.description
                    head, data = peremen(data, head)
        return head, data
    except:
        return


def sql_drv_id(driver_id):
    try:
        with connect(
                host=Con_vert.host,
                port=Con_vert.port,
                user=Con_vert.user,
                password=Con_vert.password
            ) as con:

            with con.cursor() as cursor:
                sql = """ 
                SELECT 
                id
                FROM facts.FS_Drivers drv
                WHERE ext_id=%s
                """
                cursor = con.cursor()
                cursor.execute(sql, (driver_id,))
                data = cursor.fetchall()
        return data
    except:
        return
