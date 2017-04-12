from django.conf.urls import url, include
from django.contrib import admin

from judge.ui import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.indexView),
    url(r'^api/', include('judge.api.urls')),
    url(r'^tasklist', views.tasklistView),
    url(r'^tasks/new$', views.tasknewView),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})$', views.taskView),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})/edit$', views.taskeditView),
    url(r'^auth/logout', views.logoutView),
    url(r'^auth/login', views.loginView),
    url(r'^user/(?P<username>[a-z]{1,20})$', views.userPageView),
]
