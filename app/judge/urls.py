from django.conf.urls import url, include
from django.contrib import admin

from judge.ui import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/logout$', views.logoutView),
    url(r'^auth/login$', views.loginView),
    url(r'^api/', include('judge.api.urls')),
    url(r'^', views.indexView),
]
