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

def pands_drv_df (df,drv):
    drv_df=df[drv]
    drv_df=drv_df.drop_duplicates()

    drv_df=drv_df.T
    drv_df=drv_df.reset_index()
    drv_df.columns=drv_df.iloc[0]
    drv_df=drv_df.iloc[1:]
    return drv_df 

class table_per():
    df =pandas_csv()
    PAGE_SIZE = 10
    drv=['Имя водителя','ИД водителя','Телефон водителя','Почта водителя','Промо водителя']
    drv_solo=['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок','ИД поездки','Адрес подачи','Конечный адрес','Старт поездки','Время окончания поездки','Подача','Время заказа','Промо','Номинал промокода','Статус поездки']                    
    custoner=['Имя клиента','ИД клиента','Телефон клиента','Почта клиента','Стасус','Кол поездок клиента','Дуэт','Доля совместных поездок']
    drv_df=pands_drv_df(df,drv)

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
    app.layout = html.Div( #1
        [html.Div( [

        ]),

        html.Div([ #2
                html.Div(     #2-1
                        [dash_table.DataTable(
                                            id='table',
                                            columns=[{"name": i, "id": i} for i in table_per.drv_df.columns],
                                            data=table_per.drv_df.to_dict('records'),
                                            style_cell={
                                                        'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '220px',
                                                        'whiteSpace': 'normal'
                                                        }
                        ) ] ,
                    id='left_zon',
                    style={'width':'35%',
                    'height':'auto',
                    'overflow':'auto',
                    'float':'left' },),#2-1 end
                html.Div(  #2-2
                        [dcc.Textarea(
                            
                            value='This is a TextArea component',
                            style={'width': '90%'}
                    ) ] ,
                    id='right_zon',
                    style={'width':'35%',
                    'height':'auto',
                    'overflow':'auto'},) #2-2 end
        ]), #2 end

        
        html.Div([    # 3
        dash_table.DataTable(
        id='table-sorting-filtering',
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in sorted(table_per.df.columns)
        ],
        page_current= 0,
        page_size= table_per.PAGE_SIZE,
        page_action='custom',



        sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        style_cell={
            'height': 'auto',
            'minWidth': '0px', 'maxWidth': '220px',
            'whiteSpace': 'normal'
        })
        ])  # 3 end
        ]) # 1 end








    @app.callback(
        Output('table-sorting-filtering', 'data'),
        [Input('table-sorting-filtering', "page_current"),
        Input('table-sorting-filtering', "page_size"),
        Input('table-sorting-filtering', 'sort_by')])
    def update_table(page_current, page_size, sort_by):
         
        if len(sort_by):
            dff = table_per.df.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
                inplace=False
            )
        else:
            # No sort is applied
            dff = table_per.df

        return dff.iloc[
            page_current*page_size:(page_current+ 1)*page_size
        ].to_dict('records')



    return app


if __name__ == '__main__':
    app = _create_app()
    app.run_server()


            input2=input2.replace(" ",'')
            
            try:
                if input2 =="":
                    print('asasa')
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
                    dff=table_per.df.loc[(table_per.df['ИД поездки'] == input2 ) | (table_per.df['ИД клиента'] == input2)]
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