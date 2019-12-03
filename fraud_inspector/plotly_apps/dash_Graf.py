import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from datetime import datetime,timedelta

import pandas as pd

from  django.apps  import apps

from django_plotly_dash import DjangoDash



def fraud_inspector_FraudOrders(city ,start_date,end_date):
    FraudOrders=apps.get_model('fraud_inspector','FraudOrders')
    head=[]
    for e in FraudOrders._meta.get_fields():
        head.append((str(e)).replace("fraud_inspector.FraudOrders.", ''))
    if '0' in city or 0 in city:
        FraudOrder=FraudOrders.objects.filter(order_date__range=(start_date,end_date))
        FraudOrder=FraudOrder.values_list()
    else:
        FraudOrder=FraudOrders.objects.filter(launch_region_id__in=city,order_date__range=(start_date,end_date))
        FraudOrder=FraudOrder.values_list()     
    FraudOrder=pd.DataFrame(FraudOrder,columns=head)
    FraudOrder['order_date']=pd.to_datetime(FraudOrder['order_date'], errors='coerce')
    FraudOrder['order_date']=FraudOrder['order_date'].dt.date
    FraudOrder=FraudOrder[['order_date','resolution']]
    FraudOrder=FraudOrder.groupby(['order_date','resolution']).size().reset_index(name='resolution_count')
    FraudOrder=FraudOrder.sort_values(['order_date'], ascending = [1])
    FRAUD_NO=FraudOrder.loc[(FraudOrder['resolution'] == 'FRAUD NO')]
    FRAUD_YES=FraudOrder.loc[(FraudOrder['resolution'] == 'FRAUD YES')]
    x_n=FRAUD_NO['order_date'].values.tolist()
    y_n=FRAUD_NO['resolution_count'].values.tolist()
    x_y=FRAUD_YES['order_date'].values.tolist()
    y_y=FRAUD_YES['resolution_count'].values.tolist()

    return x_n,y_n,x_y,y_y

def fraud_inspector_option_city():
    option_citys=apps.get_model('fraud_inspector','option_city')
    option_city=option_citys.objects.all()
    option_city=option_city.values_list()
    return option_city



class per_fraud_inspector():
    option_city = fraud_inspector_option_city()
    



labels = {'Point 1': (3.5,5), 'Point 2': (1.5,2), 'Point 3': (3.5,8)}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css']

app = DjangoDash('Fraf_dash_fols')


app.layout = html.Div([
    dcc.Dropdown(id='city',
    options=[{'label': i[1], 'value': i[2]} for i in fraud_inspector_option_city()]
    ,multi=True,value='0'),
    dcc.DatePickerRange(id='input1',display_format='Y-M-D',start_date=(datetime.now()- timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),clearable=True,with_portal=True,),    
    html.Button('Загрузка', id='button',style={'height': 47}),
    html.Div(id='output-container-button',
             children='Enter a value and press submit')
])


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('city', 'value'),
    dash.dependencies.State('input1', 'start_date'),
    dash.dependencies.State('input1', 'end_date')])
def update_output(n_clicks,city ,start_date,end_date):
    try:
        city=list(city)
    except:
        pass 
    if len(city)==0:
        return "Город не выбран"
    if n_clicks==None:
        return
    else:
        if str(type(start_date))=='<class \'NoneType\'>':
            return "Проверить дату"
        elif str(type(end_date))=='<class \'NoneType\'>': 
            return "Проверить дату"
        else:     
            x_n,y_n,x_y,y_y=fraud_inspector_FraudOrders(city ,start_date,end_date)
            return html.Div([
            dcc.Graph(
            figure=dict(
                data=[
                    dict(
                        x=x_n,
                        y=y_n,
                        name='НЕ ФРОД',
                        marker=go.bar.Marker(
                            color='rgb(55, 83, 109)'
                        )
                    ),
                    dict(
                        x=x_y,
                        y=y_y,
                        name='ФРОД',
                        marker=go.bar.Marker(
                            color='rgb(26, 118, 255)'
                        )
                    )
                ],
                layout=dict(
                    title='FRAUD',
                    showlegend=True,
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=dict(l=40, r=0, t=40, b=30)
                )
            ),
            style={'height': 500},
            id='my-graph'
        )  
        
        ],style={'height': 800})   


if __name__ == '__main__':
    app.run_server()