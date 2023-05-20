from django.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index_views, name='home'),
    path('about/', aboutpage_views, name='about'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('addpage/', addpage_views, name='add_page'),
    path('addDrug/', addDrug_views, name='add_Drug'),
    path('addDrugGroup/', addDrugGroup_views, name='add_DrugGroup'),
    path('ml_model/<slug:ml_model_slug>/', show_model_views, name='show_model'),
]
