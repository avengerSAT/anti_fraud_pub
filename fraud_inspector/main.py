import sys

import gspread
from isoweek import Week
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from .con import Credentials,Con_vert
from contextlib import closing
from vertica_python import connect
import pandas as pd


def gcc():
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(Credentials.credentials, scope)

    gc = gspread.authorize(credentials)
    return gc

def Update(week, year, city,city_bonus_plan_dict,city_gspread_key):
    week, year, city, date_from, date_to, name_sheet,min_trips_for_bonus = [i for i in prepareData(city, week, year,city_bonus_plan_dict)]
    wks = conn(city,city_gspread_key)
    createTable(wks, name_sheet)
    total_fraud_table, fraud_detalization_table = [i for i in loadData(date_from, date_to, city, week, year, min_trips_for_bonus,city_bonus_plan_dict)]
#    print(name_sheet, total_fraud_table, fraud_detalization_table, wks)
    updateGspread(name_sheet, total_fraud_table, fraud_detalization_table, wks)

def prepareData(city, week, year,city_bonus_plan_dict):
    city = str(city)
    date_from, date_to = Week(int(year), int(week)).monday().strftime('%Y%m%d'),Week(int(year),int(week)).sunday().strftime('%Y%m%d')
    
    name_sheet = date_from[:4] + '.' + date_from[4:6] + '.' + date_from[6:] + ' - ' + date_to[:4] + '.' + date_to[4:6] + '.' + date_to[6:]

    min_trips_for_bonus = city_bonus_plan_dict[-1][0]
    return week, year, city, date_from, date_to, name_sheet, min_trips_for_bonus


def conn(city,city_gspread_key):
    for i in city_gspread_key:
        if i[1]==city:
            gspread_key=i[2]
    gc=gcc()       
    return gc.open_by_key(gspread_key)

def createTable(wks, name_sheet):
    check_worksheet_name = 0
    for i in wks.worksheets():
        if i.title != name_sheet:
            pass
        else:
            check_worksheet_name = 1

    if check_worksheet_name == 1:
        pass
    else:
        wks.duplicate_sheet(wks.worksheet('шаблон').id,
                            new_sheet_name=name_sheet)


def loadData(date_from, date_to, city, week, year, min_trips_for_bonus,city_bonus_plan_dict):
    total_fraud_table = TotalFraudTable(date_from, date_to, city, week, year, min_trips_for_bonus,city_bonus_plan_dict).values.tolist()

    drv_ids = [0, 0]
    for i in total_fraud_table:
        if i[8] != 0:
            drv_ids.append(i[1])
    drv_ids = tuple(drv_ids)

    fraud_detalization_table = FraudDetalizationTable(date_from, date_to, city, drv_ids).values.tolist()
    return total_fraud_table, fraud_detalization_table

def TotalFraudTable(date_from, date_to, city_id, week, year, min_trips_for_bonus,city_bonus_plan_dict):
    _date_from = str(date_from)
    _date_to = str(date_to)
    _city_id = str(city_id)
    _week = str(week)
    _year = str(year)
    _min_trips_for_bonus = min_trips_for_bonus
    with closing(connect(host=Con_vert.host,
                         port=Con_vert.port,
                         user=Con_vert.user,
                         password=Con_vert.password,
                         data_base=Con_vert.data_base,
                         read_timeout=Con_vert.read_timeout)
                 ) as con:


        with open('./fraud_inspector/Sql/TotalFraudTable.sql', 'r') as sql:
            df = pd.read_sql_query(sql.read(), con, params=[_date_from, _date_to, _city_id, _week, _year, _min_trips_for_bonus])
        
        df.loc[df['Успешных поездок'] >= city_bonus_plan_dict[0][0], 'Получен бонус план'] = city_bonus_plan_dict[0][1]
        for i in city_bonus_plan_dict:
            df.loc[df['Успешных поездок'] < i[0],
                   'Получен бонус план'] = i[2]

        df.loc[df['Успешных за вычетом фродовых'] >=
               city_bonus_plan_dict[0][0], 'К списанию'] = 0
        for i in city_bonus_plan_dict:
            df.loc[df['Успешных за вычетом фродовых'] < i[0],'К списанию'] = df['Получен бонус план'] - i[2]
        df = df.drop_duplicates(subset=['Длинный позывной', 'Короткий позывной'], keep='first')
        return df


def FraudDetalizationTable(date_from, date_to, city_id, drv_ids):
    _date_from = str(date_from)
    _date_to = str(date_to)
    _city_id = str(city_id)
    _drv_ids = drv_ids
    with closing(connect(host=Con_vert.host,
                         port=Con_vert.port,
                         user=Con_vert.user,
                         password=Con_vert.password,
                         data_base=Con_vert.data_base,
                         read_timeout=Con_vert.read_timeout)
                 ) as con:


        with open('./fraud_inspector/Sql/FraudDetalizationTable.sql', 'r') as sql:
            df = pd.read_sql_query(sql.read(), con, params=[_date_from, _date_to, _city_id, _drv_ids])
        
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[1:2] + cols[0:1]
        df = df[cols]
        
        return df





def updateGspread(name_sheet, total_fraud_table, fraud_detalization_table, wks):
    wks.values_update(
        name_sheet + '!A4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': total_fraud_table
        }
    )

    wks.values_update(
        name_sheet + '!K4',
        params={
            'valueInputOption': 'USER_ENTERED'
        },
        body={
            'values': fraud_detalization_table
        }
    )



