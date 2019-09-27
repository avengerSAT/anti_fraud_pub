from django.urls import path, include
from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from check.views import dash, dash_ajax 

 

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^', include('menu.urls')),
    url('check/', include('check.urls')),
    url(r'^dash', dash,name='dash_drv_url'),
    url(r'^_dash', dash_ajax ),
    url('^', include('fraud_inspector.urls'))
]
