from contextlib import closing
from vertica_python import connect
import pandas as pd
from .con import Con_vert  

#CityDict


def TotalFraudTable(date_from, date_to, city_id, week, year, min_trips_for_bonus):
    _date_from = date_from
    _date_to = date_to
    _city_id = city_id
    _week = week
    _year = year
    _min_trips_for_bonus = min_trips_for_bonus
    with closing(connect(host=Con_vert.host,
                         port=Con_vert.port,
                         user=Con_vert.user,
                         password=Con_vert.password,
                         data_base=Con_vert.data_base,
                         read_timeout=Con_vert.read_timeout)
                 ) as con:


        with open('./fraud_inspector/sql/TotalFraudTable.sql', 'r') as sql:
            df = pd.read_sql_query(sql.read(), con, params=[_date_from, _date_to, _city_id, _week, _year, _min_trips_for_bonus])

        df.loc[df['Успешных за вычетом фродовых'] >= CityDict.city_bonus_plan_dict[_city_id][0][0], 'К списанию'] = 0
        for i in CityDict.city_bonus_plan_dict[_city_id]:
            df.loc[df['Успешных за вычетом фродовых'] < i[0],
                   'К списанию'] = df['Получен бонус план'] - i[2]
        df = df.drop_duplicates(
            subset=['Длинный позывной', 'Короткий позывной'], keep='first')
        return df


def FraudDetalizationTable(date_from, date_to, city_id, drv_ids):
    _date_from = date_from
    _date_to = date_to
    _city_id = city_id
    _drv_ids = drv_ids
    with closing(connect(host=Con_vert.host,
                         port=Con_vert.port,
                         user=Con_vert.user,
                         password=Con_vert.password,
                         data_base=Con_vert.data_base,
                         read_timeout=Con_vert.read_timeout)
                 ) as con:


        with open('./fraud_inspector/sql/FraudDetalizationTable.sql', 'r') as sql:
            df = pd.read_sql_query(
                sql.read(), con, params=[_date_from, _date_to, _city_id, _drv_ids])

        cols = df.columns.tolist()
        cols = cols[-1:] + cols[1:2] + cols[0:1]
        df = df[cols]
        return df
