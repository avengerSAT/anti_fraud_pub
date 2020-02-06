from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from fraud_inspector.plotly_apps import dash123
from fraud_inspector.plotly_apps import dash_Graf


urlpatterns = [
#    path('',views.MAIN.as_view(),name='prover'),option_city_trips
    path('gr_dash',views.test_qwe.as_view(),name='dash_gr_url'),
    path('test',views.test_123.as_view(),name='test_url'),
    path('zagr_tr',views.zagr_tr.as_view(),name='zagr_tr_url'),
    path('prov_dop',views.prov_dop.as_view(),name='prov_dop_url'),
    path('google_Sheet',views.google__Sheet.as_view(),name='google_Sheet_url'),
    path('test_map',views.test_map.as_view(),name='test_map_url'),
    path('city_option',views.city_option.as_view(),name='city_option_url'),
    path('fraud_inspector_ver_2',views.fraud_inspector_ver_2.as_view(),name='fraud_inspector_ver_2_url'),
    path('Fraud_inspector',views.Fraud_inspector.as_view(),name='Fraud_inspector_url'),
    path('auto_update_test',views.auto_update_test.as_view(),name='auto_update_test_url'),
    url(r'^frod_prov/',views.frod_prov,name='frod_prov_URL'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


