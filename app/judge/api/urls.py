from django.conf.urls import url
from judge.api import views

urlpatterns = [
    url(r'^tasks$', views.TasksListView.as_view()),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})$', views.TaskView.as_view()),
    url(r'^tasks/(?P<task_id>[0-9]{1,10})/check$', views.TaskCheckView.as_view()),
    url(r'^solutions$', views.SolutionsListView.as_view()),
    url(r'^users/(?P<username>[a-z0-9]{0,50})$', views.UserPageView.as_view()),
    url(r'^users$', views.UsersView.as_view()),
    url(r'^im$', views.IMView.as_view()),
    url(r'^comments$', views.CommentsView.as_view()),
    url(r'^comments/(?P<comment_id>[0-9]{1,10})', views.CommentView.as_view()),
    url(r'^tests/generate$', views.TestsGenerateView.as_view()),
    url(r'^tests/checker$', views.TestsCheckerView.as_view()),
]
