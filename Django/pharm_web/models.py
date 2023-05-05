from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# Импорт модуля models из библиотеки Django
from django.db import models
from django.urls import reverse


class DrugGroup(models.Model):
    title = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('DrugGroup', kwargs={'DrugGroup_id': self.id})


class Drug(models.Model):
    name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    pg = models.ForeignKey('DrugGroup', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Drug', kwargs={'Drug_id': self.pk})


class UserGroupAll(models.Model):
    group_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.group_name

    def get_absolute_url(self):
        return reverse('UserGroupAll', kwargs={'UserGroupAll_id': self.id})


class UserInGroup(models.Model):
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse('UserInGroup', kwargs={'UserInGroup_id': self.id})


class ml_model(models.Model):
    name_model = models.CharField(max_length=255)
    description = models.TextField()
    autor = models.CharField(max_length=255)
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_model

    def get_absolute_url(self):
        return reverse('ml_model', kwargs={'ml_model_id': self.pk})
