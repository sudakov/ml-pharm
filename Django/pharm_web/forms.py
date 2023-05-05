from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *

"""
class AddPgForm(forms.Form):
    title = forms.CharField(max_length=255, label="Название параметрического графа", widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = ParametricGraph
        fields = ('title')


class AddLayerForm(forms.Form):
    name = forms.CharField(max_length=255, label="Название слоя", widget=forms.TextInput(attrs={'class': 'form-input'}))
    pg = forms.ModelChoiceField(queryset=ParametricGraph.objects.all(), label="Графы", empty_label="Граф не выбран")

    class Meta:
        model = Layer
        fields = ('title')


class AddNodeForm(forms.Form):
    name_node = forms.CharField(max_length=255, label="Значение", widget=forms.TextInput(attrs={'class': 'form-input'}))
    parametr = forms.CharField(max_length=255, label="Вес вершины", widget=forms.TextInput(attrs={'class': 'form-input'}))
    layer = forms.ModelChoiceField(queryset=Layer.objects.all(), label="Категории", empty_label="Параметр не выбран")

"""


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
