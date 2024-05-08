
from django.urls import path, include
from . import  views
urlpatterns=[
    path("",views.home, name="home"),
    path("git_demo",views.gitcommands,name="gitcommands")
]
