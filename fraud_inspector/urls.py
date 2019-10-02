from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
#    path('',views.MAIN.as_view(),name='prover'),
    path('zagr_tr',views.zagr_tr.as_view(),name='zagr_tr_url'),
    path('Fraud_inspector',views.Fraud_inspector.as_view(),name='Fraud_inspector_url'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
