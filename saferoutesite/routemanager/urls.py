from django.urls import path
from . import views

urlpatterns = [
    path('', views.plot_route, name = 'plot_route')
              ]