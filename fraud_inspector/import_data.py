import csv,sys,os
import pandas as pd
from check.models import *




def del_head(trail):
    df = pd.read_csv(trail, header=0)

    df.to_csv(trail,header=False,index=False)



def imp_mod_city(trail):
#    del_head(trail)
    data=csv.reader(open(trail),delimiter=",")
    for row in data:
            post=City()
            post.Город=row[0]

            post.Код_Города=row[1]

            post.save()

def del_dan():
    Detalizacia.objects.all().delete()
    
def zap_det(trail):
    del_head(trail)

    del_dan()
    data=csv.reader(open(trail),delimiter=",")
    for row in data:
            if row =="":
                row[4]=0
            post=Detalizacia()
            post.Код_Города=row[0]
            post.Ид_водителя_короткий =row[1]
            post.Ид_водителя_длинный =row[2]
            post.Текущий_баланс_водителя=row[3]
            post.Начисления_на_баланс_водителя_за_текущий_период_исключая_пополнения=row[4]
            post.Размер_всех_доплат=row[5]
            post.Размер_всех_доплат_в_потенициальных_фрод=row[6]
            post.Размер_бонусов_только_из_доплат_до_минималки=row[7]
            post.Текущая_сумма_бонус_плана=row[8]

            post.save()
    os.remove(trail)        
def srav_csv(trail,trail2):
    df1=pd.read_csv(trail)
    df2=pd.read_csv(trail2)
    a=df1["ИД поездки"][~df1["ИД поездки"].isin(df2["ИД поездки"])].dropna()
    result = pd.concat([a, df1], axis=1, join_axes=[a.index])
    result.to_csv('antifraud/templates/csvV.Kondratev/trips1231.csv',index=False)
    result= result.drop(result.columns[0], axis=1)
    result.to_csv(trail,index=False)

def svrka_dan(trail,trail2):
  #  srav_csv(trail,trail2)
    del_head(trail)

    data=csv.reader(open(trail),delimiter=",")

    for row in data:
            post=trip_dan()  
            post.Дуэт=row[1]
            if row[2]=='':
              row[2]='00:00:00'
            post.Подача=row[2]
            if row[3]=='':
              row[3]='00:00:00'            
            post.Время_заказа=row[3]
            post.Время_заказа_БО=row[4]
            post.Дистанция=row[5]
            if row[6]=='':
              row[6]='0001-01-01 00:00:01'
            post.Старт_поездки=row[6]
            post.Адрес_подачи=row[7]
            if row[8]=='':
              row[8]='0001-01-01 00:00:01'            
            post.Время_окончания_поездки=row[8]
            post.Конечный_адрес=row[9]
            post.Промо=row[10]
            post.Часть_промо=row[11]
            post.Доплата=row[12]
            post.Статус_поездки=row[13]
            post.ИД_поездки=row[14]
            post.Кол_поездок_клиента=row[15]
            post.ИД_клиента=row[16]
            post.Стасус=row[17]
            post.Имя_клиента=row[18]
            post.Телефон_клиента=row[19]
            post.Почта_клиента=row[20]
            post.ИД_водителя=row[21]
            post.Имя_водителя=row[22]
            post.Телефон_водителя=row[23]
            post.Почта_водителя=row[24]
            post.Промо_водителя=row[25]
            post.Статус_р=row[26]

            post.save()
    os.remove(trail)


