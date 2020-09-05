from django.urls import path, include
from social import views
from django.conf.urls import url

urlpatterns = [
    path("", views.users, name="users"),
    path("<str:name>/", views.details, name="details"),
    # url('<str:name>/delete', views.users, name='delete')
    url(r'^delete/(?P<name>.*)/$', views.delete, name='delete'),
    path("<str:name>/instagram", views.instagram, name="instagram"),
    path("<str:name>/twitter", views.twitter, name="twitter"),
    path("<str:name>/reddit", views.reddit, name="reddit"),
    path("<str:name>/facebook", views.facebook, name="facebook"),
    path("<str:name>/stackoverflow", views.stackoverflow, name="stackoverflow"),
    path("<str:name>/pinterest", views.pinterest, name="pinterest"),
    path('get-task-info/', views.get_task_info, name="get_task_info"),
    path(r'^celery-progress/', include('celery_progress.urls')),
    path('delete_platform/<slug:name>/<slug:platform>/', views.delete_platform, name='delete_platform'),
    path("<slug:name>/timeline/<slug:platform>", views.get_timeline, name="get_timeline"),

]