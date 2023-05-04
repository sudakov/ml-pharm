from django.urls import path, re_path

from .views import *

urlpatterns = [
"""    path('', index, name='home'),
    path('about/', about, name='about'),
    path('addpage/', addpage, name='add_page'),
    path('contact/', contact, name='contact'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('pg/<int:pg_id>/', show_pg, name='pg'),
    path('add_layer', add_layer, name='add_layer'),
    path('layer/<int:layer_id>/', show_layer, name='layer'),
    path('add_node/', add_node, name='add_node'),"""
]