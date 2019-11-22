import sys
from random import randint

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output ,State

import pandas as pd
import datetime
import json
from check import views
from check import sqlvertica



 

def pandas_csv(a):
    df = pd.read_csv(a+'/Сводная_по_водителю.csv')
    try:
        df[['Дуэт','Кол поездок клиента']] = df[['Дуэт','Кол поездок клиента']].astype('int')
        df['Доля совместных поездок']=df['Дуэт']/df['Кол поездок клиента']*100
        df['Доля совместных поездок']=round(df['Доля совместных поездок'],2)
        df['Доля совместных поездок']=df['Доля совместных поездок'].astype('str')+" %"
    except:  
        df['Доля совместных поездок']=df['Дуэт']  
        df['Статус']=df['Статус']+" / "+df['Статус р']    
    df[' '] = range(1, len(df) + 1)

    return df

def pands_per (df,per):
    per_df=df[per]
    per_df=per_df.drop_duplicates()
    per_df=per_df.T
    per_df=per_df.reset_index()
    per_df.columns=per_df.iloc[0]
    per_df=per_df.iloc[1:]
    return per_df 

class table_per():
    PAGE_SIZE = 10
    drv=['ИД водителя','Имя водителя','Телефон водителя','Почта водителя','Промо водителя']
    drv_solo=[' ','Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Статус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']                    
    svod=[' ','Дуэт','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']
    custoner=['ИД клиента','Имя клиента','Телефон клиента','Почта клиента','Статус','Кол поездок клиента','Дуэт','Доля совместных поездок']
    external_scripts = ['static/js/jquery.js','static/js/jquery.dataTables.min.js','static/js/tapl.js']

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css']

def dispatcher(request,trail):
    a=trail
    app = _create_app(a)
    params = {
        'data': request.body,
        'method': request.method,
        'content_type': request.content_type
    }
    with app.server.test_request_context(request.path, **params):
        app.server.preprocess_request()
        try:
            response = app.server.full_dispatch_request()
        except Exception as e:
            response = app.server.make_response(app.server.handle_exception(e))
        return response.get_data()

def _create_app(a):
    app = dash.Dash(__name__,external_scripts=table_per.external_scripts, external_stylesheets=table_per.external_stylesheets) 
  
    app.layout = html.Div([
        html.Div([
            html.Div(
            [dcc.Input(id='input1', type='text'),
            html.Button('Загрузить данные:', id='btn-1', n_clicks_timestamp='0',title='Загружает данные из SQL')] ,
            id='left_zon',
            style={'width':'45%',
            'min-height':'50px',
            'height':'auto',
            'overflow':'auto',
            'float':'left'}),
        html.Div( 
            [dcc.Input(id='input2', type='text', debounce=True),
            html.Button('Поиск:', id='btn-2', n_clicks_timestamp='0',title='Поиск по загруженным данным.Осуществляется по ИД заказа или ИД клиента')] ,
            id='right_zon',
            style={'width':'45%',
            'min-height':'50px',
            'height':'auto',
            'overflow':'auto'},) 
                                ]),
        html.Div(
        html.Div(id='container')
                )
        
        ])                    

    @app.callback(
        Output('container', 'children'),
        [Input('btn-1', 'n_clicks_timestamp'),
        Input('btn-2', 'n_clicks_timestamp')],
        [State("input1", "value"),State("input2", "value") ])

    def displayClick(btn1, btn2, input1,input2):
       
        if int(btn1)>int(btn2):
            per_1=input1.replace(" ","")
            if per_1 =="":
                msg = 'НЕ введен ид поездки'
                return html.Div([ 
                        html.Div(msg)
                    ])
            else:
                try:
                    driver_id,customer_id,drv_id=sqlvertica.sql_trip(per_1)
                    sqlvertica.sql_old_drv(drv_id,a)
                except:
                    msg='НЕ введен ид поездки-1'
                    return html.Div([ 
                        html.Div(msg)
                    ])
                if driver_id=='Нет данных' or customer_id=='Нет данных' :
                    msg='НЕ введен ид поездки-2'
                    return html.Div([ 
                        html.Div(msg)
                    ])                       
 
                drv_df =pands_per(pandas_csv(a),table_per.drv)
                os_df=pandas_csv(a)[table_per.drv_solo]
                return html.Div([
                                html.Div([
                                html.Div(dash_table.DataTable(
                                            id='table',
                                            columns=[{"name": i, "id": i} for i in  drv_df.columns],
                                            data= drv_df.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                        ) ,
                    id='left_zon',
                    style={'width':'35%',
                    'height':'auto',
                    'overflow':'auto',
                    'float':'left'}),

                                        ]),
                                html.Div(
                    dash_table.DataTable(
                                        id='pricetable-1',
                                        columns=[{"name": i, "id": i} for i in os_df.columns],
                                        data=os_df.to_dict('records'),
                                        page_current= 0,
                                        page_size= table_per.PAGE_SIZE,
                                        
                                        style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '230px',
                                                        'whiteSpace': 'normal'
                                                    }
                                        )
                                        )
                                
                                ])
        else:
            per_2=input2.replace(" ","")  
            if per_2 =="": 
                drv_df =pands_per(pandas_csv(a),table_per.drv)
                os_df=pandas_csv(a)[table_per.drv_solo]
                return html.Div([
                                html.Div([
                                html.Div(dash_table.DataTable(
                                            id='table',
                                            columns=[{"name": i, "id": i} for i in  drv_df.columns],
                                            data= drv_df.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                        ) ,
                    id='left_zon',
                    style={'width':'35%',
                    'height':'auto',
                    'overflow':'auto',
                    'float':'left'}),

                                        ]),
                                html.Div(
                    dash_table.DataTable(
                                        id='pricetable-1',
                                        columns=[{"name": i, "id": i} for i in os_df.columns],
                                        data=os_df.to_dict('records'),
                                        page_current= 0,
                                        page_size= table_per.PAGE_SIZE,
                                        style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '230px',
                                                        'whiteSpace': 'normal'
                                                    }
                                        )
                                        )
                                
                                ])
            else:
                dff=pandas_csv(a).loc[(pandas_csv(a)['ИД поездки'] == per_2 ) | (pandas_csv(a)['ИД клиента'] == per_2)]
                drv_df =pands_per(pandas_csv(a),table_per.drv)
                cus_dff=pands_per(dff,table_per.custoner)

                dff_sv=dff[table_per.svod]
                return  html.Div([
                                html.Div([
                                html.Div(dash_table.DataTable(
                                            id='table_c',
                                            columns=[{"name": i, "id": i} for i in  cus_dff.columns], 
                                            data= cus_dff.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                                                                ) ,
                                    id='left_zon',
                                    style={'width':'35%',
                                    'height':'auto',
                                    'overflow':'auto',
                                    'float':'left'}),
                                html.Div( dash_table.DataTable(
                                            id='table_d',
                                            columns=[{"name": i, "id": i} for i in drv_df.columns],
                                            data= drv_df.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                                                                ) ,
                                    id='right_zon',
                                    style={'width':'50%',
                                    'height':'auto',
                                    'overflow':'auto'},) 
                                                        ]),
                                html.Div(
                    dash_table.DataTable(
                                        id='pricetable-1',
                                        columns=[{"name": i, "id": i} for i in dff_sv.columns],
                                        data=dff_sv.to_dict('records'),
                                        page_current= 0,
                                        page_size= table_per.PAGE_SIZE,
                                        style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '230px',
                                                        'whiteSpace': 'normal'
                                                    }
                                        )
                                        )
                                
                                ])                   

    return app                    


            

if __name__ == '__main__':
    app = _create_app(a)
    app.run_server()
                  
