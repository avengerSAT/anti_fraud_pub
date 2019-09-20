from django.urls import path, include
from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    url('^', include('django.contrib.auth.urls')),
    url('^', include('menu.urls')),
    url('check/', include('check.urls')),
   # path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
