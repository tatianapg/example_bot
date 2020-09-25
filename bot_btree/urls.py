#urls para la aplicacion bot_btree
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
