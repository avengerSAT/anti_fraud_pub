import sys
from random import randint

import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as dhc
import dash_html_components as html

import pandas as pd

def pandas_csv():
    df = pd.read_csv('/home/vkondratev/anti_fraud/check/templates/csvvkondratev/Сводная_по_водителю.csv')
    try:
        df[['Дуэт','Кол поездок клиента']] = df[['Дуэт','Кол поездок клиента']].astype('int')
        df['Доля совместных поездок']=df['Дуэт']/df['Кол поездок клиента']*100
        df['Доля совместных поездок']=df['Доля совместных поездок'].astype('str')+" %"
    except:  
        df['Доля совместных поездок']=df['Дуэт']  
        df['Стасус']=df['Стасус']+" / "+df['Статус р']    
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
    df =pandas_csv()
    PAGE_SIZE = 10
    drv=['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']
    drv_solo=[' ','Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']                    
    svod=[' ','Дуэт','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']
    custoner=['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок']






def dispatcher(request):
    app = _create_app()
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

def _create_app():
    app = dash.Dash()
    app.layout = html.Div([
        html.Div([dcc.Input(id='input-box', type='text'),
        html.Button('ПОИСК', id='button')]),
        html.Div(id='output-container-button',
                children='')
    ])







    @app.callback(
        dash.dependencies.Output('output-container-button', 'children'),
        [dash.dependencies.Input('button', 'n_clicks')],
        [dash.dependencies.State('input-box', 'value')])
    def update_output(n_clicks,value):
        value=value.replace(" ",'')
        try:
            if value =="":
                drv_df =pands_per(table_per.df,table_per.drv)
                os_df=table_per.df[table_per.drv_solo]
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
                                        id='table',
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
                dff=table_per.df.loc[(table_per.df['ИД поездки'] == value ) | (table_per.df['ИД клиента'] == value)]
                drv_df =pands_per(table_per.df,table_per.drv)
                cus_dff=pands_per(dff,table_per.custoner)
                dff_sv=dff[table_per.svod]
                return  html.Div([
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
                                html.Div( dash_table.DataTable(
                                            id='table',
                                            columns=[{"name": i, "id": i} for i in cus_dff.columns],
                                            data= cus_dff.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                                                                ) ,
                                    id='right_zon',
                                    style={'width':'35%',
                                    'height':'auto',
                                    'overflow':'auto'},) #2-2 end
                                                        ]),
                                html.Div(
                    dash_table.DataTable(
                                        id='table',
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
        except:
            return 'Введены не верные данные'.format()
 

      


    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server()