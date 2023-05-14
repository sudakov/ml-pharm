from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('about/', aboutpage, name='about'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('addpage/', addpage, name='add_page'),
    path('addDrugGroup/', addDrugGroup, name='add_DrugGroup'),
    path('ml_model/<slug:ml_model_slug>/', show_model, name='show_model'),
]
