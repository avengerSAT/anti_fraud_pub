import csv
import os
from csv import writer

import pandas as pd
import vertica_python
from vertica_python import connect

from .con import Con_vert


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

            with open('./Sql/sql_trip.sql', 'r') as sql:
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


def sql_prov(customer_id, driver_id, drv_id):
    conn_info = {
        'host': Con_vert.host,
        'port': Con_vert.port,
        'user': Con_vert.user,
        'password': Con_vert.password
    }

    with connect(**conn_info) as conn:
        with conn.cursor() as cur:

            with open('./Sql/sql_prov-customer_data.sql', 'r') as customer_data:
                cur.execute(customer_data.read(), (customer_id,))
                data = cur.fetchall()
                head = cur.description
                cus_head, cus = peremen(data, head)
            
            with open('./Sql/sql_prov-driver_data.sql', 'r') as driver_data:
                cur.execute(driver_data.read(), (driver_id,))
                data = cur.fetchall()
                head = cur.description
                drv_hed, drv = peremen(data, head)
                
            with open('./Sql/sql_prov-customer_trips_total_data.sql', 'r') as customer_trips_total_data:    
                cur.execute(customer_trips_total_data.read(), (customer_id, customer_id))
                data = cur.fetchall()
                head = cur.description
                svod_cus_head, svod_cus = peremen(data, head)
                
            with open('./Sql/sql_prov-customer_driver_duet_data.sql', 'r') as customer_driver_duet_data:    
                cur.execute(customer_driver_duet_data.read(), (driver_id, customer_id, drv_id))
                data = cur.fetchall()
                head = cur.description
                svod_drv_cus_head, svod_drv_cus = peremen(data, head)
    return cus_head, cus, drv_hed, drv, svod_cus_head, svod_cus, svod_drv_cus_head, svod_drv_cus


def sql_doplat(start_date, end_date):
    conn_info = {'host': Con_vert.host,
                 'port': Con_vert.port,
                 'user': Con_vert.user,
                 'password': Con_vert.password}
    sql_1 = """
SELECT DISTINCT
region_id as ИД_региона
,(to_timestamp(oo.order_start_date)::date)::varchar as Дата_проверки
,COUNT(dt.order_id) as Количество_поездок_с_компенсацией
,CAST(SUM(transaction_amount/100)AS DECIMAL(14,0)) as Сумма_компенсации
,CAST(SUM(case WHEN qwe.Сумма_списаний_за_поездку is NULL THEN '0' else qwe.Сумма_списаний_за_поездку end )AS DECIMAL(14,0)) as Сумма_списаний
,CAST(SUM(dt.transaction_amount/100+(case WHEN qwe.Сумма_списаний_за_поездку is NULL THEN '0' else qwe.Сумма_списаний_за_поездку end ))AS DECIMAL(14,0)) as Сумма_после_проверки
from facts.FS_Drivers_balance_transaction dt
LEFT join facts.FS_Orders oo
on dt.order_id=oo.id
left join (
SELECT DISTINCT
dt.order_id,
SUM(transaction_amount/100) as Сумма_списаний_за_поездку
from facts.FS_Drivers_balance_transaction dt
left JOIN (  SELECT
o.id as order_id
    FROM facts.FS_Orders o
    LEFT JOIN facts.FS_Fraud_orders fo
        ON o.id = fo.id
    LEFT JOIN facts.FS_Fraud_verifies fv
        ON fo.id = fv.order_id
    LEFT JOIN 
(SELECT MAX(id) id, order_pattern_id, resolution ,session_id
FROM facts.FS_Fraud_resolutions
WHERE resolution IS NOT NULL
GROUP BY order_pattern_id, resolution,session_id) fr
        ON fv.id = fr.session_id
    WHERE resolution = 'YES'
) gr_1 on gr_1.order_id=dt.order_id
WHERE transaction_type='Order Refund'
and gr_1.order_id is not NULL
GROUP BY dt.order_id  ) qwe on qwe.order_id= dt.order_id
WHERE 1=1
 	 AND transaction_type='Compensation'
 	 AND to_timestamp(oo.order_start_date)::date is not NULL
 	 AND to_timestamp(oo.order_start_date)::date >= %s
 	 AND to_timestamp(oo.order_start_date)::date <= %s
group by region_id, Дата_проверки
        """
    with connect(**conn_info) as conn:
        cur = conn.cursor()
        cur.execute(sql_1, (start_date, end_date))
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
        sql = """ 
select DISTINCT
gr.trip_number as Дуэт
,(to_timestamp(oo.arrive_time)-to_timestamp(oo.accept_time))::varchar as  Подача
,to_timestamp(oo.order_start_date) as Старт_поездки
,oo.order_src_address as Адрес_подачи
,to_timestamp(oo.order_end_date) as Время_окончания_поездки
,oo.order_dst_address as Конечный_адрес
,oo.promo_code_description as Промо
,oo.promo_code_discount/100 as Номинал_промокода
,(to_timestamp(oo.order_end_date)-to_timestamp(oo.order_start_date))::varchar as Время_заказа
,oo.sub_state as Статус_поездки
,oo.id as ИД_поездки
,grs.trip_number as Кол_поездок_клиента
,oo.customer_id as ИД_клиента
,cc.status as Стасус
,case WHEN cc.last_name is not NULL THEN (cc.last_name::varchar)||' '||(cc.first_name ::varchar) else cc.first_name end Имя_клиента
,cc.phone AS Телефон_клиента
,cc.email AS Почта_клиента
,(drv.id::varchar)||'  /  '||(drv.ext_id::varchar) as ИД_водителя
,case WHEN pr.last_name is not NULL THEN (pr.first_name::varchar)||' '||(pr.last_name ::varchar) else pr.first_name end Имя_водителя
,prs.email as Почта_водителя
,pr.phone AS Телефон_водителя
,drv.promo_code AS Промо_водителя
,case when cc.status_reasons is NULL Then ' ' ELSE cc.status_reasons end Статус_р
FROM facts.FS_Orders oo
LEFT JOIN facts.FS_Drivers drv ON oo.driver_id=drv.id
LEFT JOIN facts.FS_Profiles pr ON drv.profile_id = pr.id
LEFT JOIN facts.FS_Profiles_security prs ON pr.id = prs.id
LEFT JOIN facts.FS_Customers cc ON cc.id=oo.customer_id
LEFT JOIN facts.FS_Orders_customer_cost oc ON oc.order_id=oo.id
LEFT JOIN (SELECT customer_id, count (*) as trip_number FROM facts.FS_Orders WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') 
 group by customer_id ) grs on grs.customer_id=oo.customer_id
LEFT JOIN (SELECT  DISTINCT 
customer_id, driver_id, count(*) as trip_number
FROM facts.FS_Orders 
WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') and driver_id=%s
GROUP BY customer_id, driver_id) gr ON gr.driver_id = oo.driver_id and gr.customer_id = oo.customer_id
WHERE (sub_state = 'ORDER_COMPLETED' OR sub_state = 'CUSTOMER_CANCEL_AFTER_TRIP') and oo.driver_id=%s
                """

        cursor = con.cursor()
        cursor.execute(sql, (drv_id, drv_id,))
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
        sql = """ 
SELECT
gr.qwe as Количество_успешных_заказов
,gr_1.qwer as Количество_заказов_отмеченных_как_фрод
,gr.qwe-gr_1.qwer as Количество_поездок_без_нарушений 
from 
(SELECT 
driver_id
,count(id) as qwe
FROM facts.FS_Orders oo 
WHERE 1=1
	AND sub_state = 'ORDER_COMPLETED'
	 AND driver_id = %s
 	 AND to_timestamp(oo.order_end_date)::date >=%s
 	 AND to_timestamp(oo.order_end_date)::date <=%s
GROUP By driver_id) gr 
left join (
  SELECT
        COUNT(DISTINCT o.id) AS qwer
        , o.driver_id
    FROM facts.FS_Orders o
    LEFT JOIN facts.FS_Fraud_orders fo
        ON o.id = fo.id
    LEFT JOIN facts.FS_Fraud_verifies fv
        ON fo.id = fv.order_id
    LEFT JOIN 
(SELECT MAX(id) id, order_pattern_id, resolution ,session_id
FROM facts.FS_Fraud_resolutions
WHERE resolution IS NOT NULL
GROUP BY order_pattern_id, resolution,session_id) fr
        ON fv.id = fr.session_id
where  fr.resolution='YES'
and o.driver_id=%s
and to_timestamp(fo.order_date)::date >=%s
and to_timestamp(fo.order_date)::date <=%s
GROUP BY o.driver_id
) gr_1 on gr_1.driver_id =gr.driver_id
                """
        cursor = con.cursor()
        cursor.execute(sql, (driver_id, start_date, end_date,
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
        sql = """ 
SELECT 
id
FROM facts.FS_Drivers drv
WHERE ext_id=%s
                """
        cursor = con.cursor()
        cursor.execute(sql, (driver_id,))
        data = cursor.fetchall()
        cursor.close()
        con.close()
        return data
    except:
        con.close()
        return
