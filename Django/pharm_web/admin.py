# Импорт модуля admin из библиотеки Django.contrib
from django.contrib import admin
# Импорт модели MyModel из текущего каталога (".")
from .models import *

# Регистрация модели MyModel для административного сайта
admin.site.register(ml_model)
admin.site.register(UserGroupAll)
admin.site.register(UserInGroup)
admin.site.register(Drug)
admin.site.register(DrugGroup)