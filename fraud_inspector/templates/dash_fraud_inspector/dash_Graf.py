import sys
from random import randint

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output ,State

from  django.apps  import apps

import pandas as pd
import datetime
import json
from check import views






def dan_prov_ ():
    FraudOrder=apps.get_model('fraud_inspector','FraudOrders')
    FraudOrder=FraudOrder.objects.all()
    return FraudOrder



def dan_City_ ():
    City=apps.get_model('fraud_inspector','option_city')
    City=City.objects.all()
    return City


class per_dash_graf():
    FraudOrder=dan_prov_()
    city=dan_City_()



    
def dispatcher(request,fraim):
    pass