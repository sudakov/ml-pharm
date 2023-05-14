from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# Импорт модуля models из библиотеки Django
from django.db import models
from django.urls import reverse


class DrugGroup(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название группы")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('DrugGroup', kwargs={'DrugGroup_slug': self.slug})

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['title']


class Drug(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название лекарственного средства')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    pg = models.ForeignKey('DrugGroup', null=True, on_delete=models.CASCADE,
                           verbose_name='Группа лекарственных средств')
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Drug', kwargs={'Drug_slug': self.slug})

    class Meta:
        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['name']


class UserGroupAll(models.Model):
    group_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.group_name

    def get_absolute_url(self):
        return reverse('UserGroupAll', kwargs={'UserGroupAll_slug': self.slug})


class UserInGroup(models.Model):
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse('UserInGroup', kwargs={'UserInGroup_slug': self.slug})


class ml_model(models.Model):
    name_model = models.CharField(max_length=255, verbose_name="Название модели")
    description = models.TextField(verbose_name="Описание модели")
    autor = models.CharField(max_length=255, verbose_name="Автор")
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name_model

    def get_absolute_url(self):
        return reverse('show_model', kwargs={'ml_model_slug': self.slug})

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ['time_update']


class DrugInteractionTable(models.Model):
    DrugOne = models.ForeignKey('Drug', null=True, on_delete=models.CASCADE, verbose_name='ЛС №1', related_name='druginteractions_one')
    DrugTwo = models.ForeignKey('Drug', null=True, on_delete=models.CASCADE, verbose_name='ЛС №2', related_name='druginteractions_two')
    Interaction = models.TextField(verbose_name="Взаимодействие")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.Interaction

    def get_absolute_url(self):
        return reverse('DrugInteractionTable', kwargs={'DrugInteractionTable_slug': self.slug})

    class Meta:
        verbose_name = 'Взаимодействие ЛС (Таблица)'
        verbose_name_plural = 'Взаимодействие ЛС (Таблица)'
        ordering = ['DrugOne']
