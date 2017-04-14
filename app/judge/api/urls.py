from django.conf.urls import url
from judge.api import views

urlpatterns = [
    url(r'^tasks$', views.TasksListView.as_view()),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})$', views.TaskView.as_view()),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})/check$', views.TaskCheckView.as_view()),
    url(r'^queue/(?P<qid>[0-9a-z-]{36})$', views.QueueView.as_view()),
    url(r'^solutions$', views.SolutionsListView.as_view()),
]