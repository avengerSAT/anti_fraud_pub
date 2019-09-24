import vertica_python
from vertica_python import connect
from csv import writer
import pandas as pd
import csv
import os
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
        con = connect(
            host=Con_vert.host,
            port=Con_vert.port,
            user=Con_vert.user,
            password=Con_vert.password)


        cursor = con.cursor()
        cursor.execute(sql_vert.sql, (trail,))
        data = cursor.fetchall()

        # переменная водитель
        driver_id = data[0][0]
        # переменная клиент
        customer_id = data[0][1]
        # переменная водитель корот
        drv_id = data[0][2]
        con.close()
        return driver_id, customer_id, drv_id
    except:
        con.close()
        driver_id, customer_id, drv_id = "Нет данных", "Нет данных", "Нет данных"
        return driver_id, customer_id, drv_id

def sql_prov(customer_id, driver_id, drvr_id,chek_box):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(sql_vert.sql_1, (customer_id,))
        data = cur.fetchall()
        head = cur.description
        cus_head, cus = peremen(data, head)
        cur.execute(sql_vert.sql_2, (driver_id,))
        data = cur.fetchall()
        head = cur.description
        drv_hed, drv = peremen(data, head)
        cur.execute(sql_vert.sql_3, (customer_id, customer_id))
        data = cur.fetchall()
        head = cur.description
        svod_cus_head, svod_cus = peremen(data, head)
        if chek_box=='yes':
            cur.execute(sql_vert.sql_5, (driver_id,customer_id,drvr_id))
            data = cur.fetchall()
            head = cur.description
            svod_drv_cus_head, svod_drv_cus = peremen(data, head)
        else:
            cur.execute(sql_vert.sql_4, (drvr_id, customer_id))
            data = cur.fetchall()
            head = cur.description
            svod_drv_cus_head, svod_drv_cus = peremen(data, head)
        cur.close
    return cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus


def sql_doplat(start_date, end_date):
    conn_info = {'host': Con_vert.host,
                 'port': Con_vert.port,
                 'user': Con_vert.user,
                 'password': Con_vert.password}
    with connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(sql_vert.sql_6, (start_date, end_date))
        data = cur.fetchall()
        head = cur.description
        head, data = peremen(data, head)
        cur.close
    return head, data


def sql_old_drv(drv_id, trail):
    try:
        con = connect(
            host=Con_vert.host,
            port=Con_vert.port,
            user=Con_vert.user,
            password=Con_vert.password
        )
        cursor = con.cursor()
        cursor.execute(sql_vert.sql_7, (drv_id, drv_id,))
        data = cursor.fetchall()
        head = cursor.description
        a, b = peremen(data, head)
        put = trail+'/Сводная_по_водителю.csv'
        save_csv(b, a, put)
        cursor.close()
        con.close()
        return
    except:
        put = trail+'/Сводная_по_водителю.csv'
        print("ytn")
        con.close()
        return


def sql_drv_poezd(driver_id, start_date, end_date):
    try:
        con = connect(
            host=Con_vert.host,
            port=Con_vert.port,
            user=Con_vert.user,
            password=Con_vert.password
        )

        cursor = con.cursor()
        cursor.execute(sql_vert.sql_8, (driver_id, start_date, end_date,
                             driver_id, start_date, end_date,))
        data = cursor.fetchall()
        head = cursor.description
        head, data = peremen(data, head)
        cursor.close()
        con.close()
        return head, data
    except:
        con.close()
        return


def sql_drv_id(driver_id):
    try:
        con = connect(
            host=Con_vert.host,
            port=Con_vert.port,
            user=Con_vert.user,
            password=Con_vert.password
        )
        cursor = con.cursor()
        cursor.execute(sql_vert.sql_9, (driver_id,))
        data = cursor.fetchall()
        cursor.close()
        con.close()
        return data
    except:
        con.close()
        return
