# Импорт модуля admin из библиотеки Django.contrib
from django.contrib import admin
# Импорт модели MyModel из текущего каталога (".")
from .models import *

# Регистрация модели MyModel для административного сайта
admin.site.register(MainTestModel)