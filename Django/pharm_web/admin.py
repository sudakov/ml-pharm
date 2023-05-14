# Импорт модуля admin из библиотеки Django.contrib
from django.contrib import admin
# Импорт модели MyModel из текущего каталога (".")
from .models import *


class ml_modelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_model', 'slug', 'autor', 'time_create', 'user_group')
    list_display_links = ('id', 'name_model', 'slug')
    search_fields = ('name_model', 'autor', 'time_create', 'user_group')
    prepopulated_fields = {"slug": ("name_model",)}


class DrugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'pg', 'time_create', 'user')
    list_display_links = ('id', 'name', 'slug')
    search_fields = ('name', 'time_create', 'user')
    prepopulated_fields = {"slug": ("name",)}


class DrugGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'time_create', 'user')
    list_display_links = ('id', 'title', 'slug')
    search_fields = ('title', 'time_create', 'user')
    prepopulated_fields = {"slug": ("title",)}


class DrugInteractionTableAdmin(admin.ModelAdmin):
    list_display = ('DrugOne', 'DrugTwo', 'Interaction', 'time_create', 'user')
    search_fields = ('DrugOne', 'DrugTwo', 'user')

# Регистрация моделей для административного сайта
admin.site.register(ml_model, ml_modelAdmin)

admin.site.register(Drug, DrugAdmin)
admin.site.register(DrugGroup, DrugGroupAdmin)

admin.site.register(DrugInteractionTable, DrugInteractionTableAdmin)

admin.site.register(UserGroupAll)
admin.site.register(UserInGroup)
