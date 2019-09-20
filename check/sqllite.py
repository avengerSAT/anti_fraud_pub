import sqlite3



def peremen(data,head):
        a=([column[0].replace("_",' ') for column in head])
        b=data 

        return a,b

        
def sqltest():
        con = sqlite3.connect("db.sqlite3") # или :memory: чтобы сохранить в RAM
        cursor = con.cursor()
        sql = """ 
        SELECT Код_Города,
Ид_водителя_короткий,
Текущий_баланс_водителя,
Начисления_на_баланс_водителя_исключая_пополнения,
Размер_всех_доплат,
Размер_всех_доплат_в_потенициальных_фрод,
Размер_бонусов_только_из_доплат_до_минималки,
Текущая_сумма_бонус_плана,
Ид_водителя_длинный 
FROM check_detalizacia
        """

        cursor.execute(sql)
        data = cursor.fetchall()
        head = cursor.description


        a,b=peremen(data,head)
        cursor.close()
        con.close() 

        return a,b


        
def sqltest1():
        con = sqlite3.connect("db.sqlite3") # или :memory: чтобы сохранить в RAM
        cursor = con.cursor()
        sql = """ 
        SELECT Город,Код_Города FROM check_city
        """

        cursor.execute(sql)
        data = cursor.fetchall()
        head = cursor.description


        a,b=peremen(data,head)
        cursor.close()
        con.close() 

        return a,b


def sql_dan(driver_id,customer_id):
        con = sqlite3.connect("db.sqlite3")
        

        cursor = con.cursor()

        sql="""
select
Дуэт,
Подача,
Время_заказа,
Время_заказа_БО,
Дистанция,
Старт_поездки,
Адрес_подачи,
Время_окончания_поездки,
Конечный_адрес,
Промо,
Часть_промо,
Доплата,
Статус_поездки,
ИД_поездки,
Кол_поездок_клиента,
ИД_клиента,
Стасус,
Имя_клиента,
Телефон_клиента,
Почта_клиента,
ИД_водителя,
Имя_водителя,
Телефон_водителя,
Почта_водителя,
Промо_водителя,
Статус_р
from check_trip_dan
where  ИД_водителя='%s' or ИД_клиента ='%s'  
"""        
        cursor.execute(sql %(driver_id,customer_id))

        data = cursor.fetchall()
        head = cursor.description
        a,b=peremen(data,head)
        con.close()
        return a,b
