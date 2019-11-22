import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd

from  django.apps  import apps

from django_plotly_dash import DjangoDash



def fraud_inspector_FraudOrders():
    FraudOrders=apps.get_model('fraud_inspector','FraudOrders')
    FraudOrder=FraudOrders.objects.all()
    FraudOrder=FraudOrder.values_list()
    head=[]
    for e in FraudOrders._meta.get_fields():
        head.append((str(e)).replace("fraud_inspector.FraudOrders.", ''))
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
    head=[]
    for e in option_citys._meta.get_fields():
        head.append((str(e)).replace("fraud_inspector.FraudOrders.", ''))
    option_city=pd.DataFrame(option_city,columns=head)
    return option_city



class per_fraud_inspector():
    option_city = fraud_inspector_option_city()
    



labels = {'Point 1': (3.5,5), 'Point 2': (1.5,2), 'Point 3': (3.5,8)}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css']
x_n,y_n,x_y,y_y=fraud_inspector_FraudOrders()
app = DjangoDash('Fraf_dash_fols')

app.layout = html.Div([

    dcc.Graph(
    figure=go.Figure(
        data=[
            go.Bar(
                x=x_n,
                y=y_n,
                name='НЕ ФРОД',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)'
                )
            ),
            go.Bar(
                x=x_y,
                y=y_y,
                name='ФРОД',
                marker=go.bar.Marker(
                    color='rgb(26, 118, 255)'
                )
            )
        ],
        layout=go.Layout(
            title='FRAUD',
            showlegend=True,
            legend=go.layout.Legend(
                x=0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    ),
    style={'height': 300},
    id='my-graph'
)  

],style={'height': 2200}
)



if __name__ == '__main__':
    app.run_server()