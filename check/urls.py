from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.MAIN.as_view(),name='prover'),
    path('Fraud_PROV',views.Fraud_PROV.as_view(),name='Fraud_PROV_url'),
    path('Driver',views.Driver.as_view(),name='Driver_url'),
    path('rez_prover',views.rez_prover.as_view(),name='rez_prover_url'),
    path('brend',views.brend.as_view(),name='brend_url'),
    path('svod_doplat',views.svod_doplat.as_view(),name='svod_doplat_url'),
    url(r'^Driver/1/',views.drvr,name='DRV_URL'),
    path('UnverifiedTripsCompensations', views.UnverifiedTripsCompensations.as_view(), name='UnverifiedTripsCompensations_url'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
