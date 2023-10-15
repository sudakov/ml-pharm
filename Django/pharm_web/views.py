from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.list import ListView
from django.db.models import Q

from .all_drug_table_views import all_drug_table
from .iteraction_medscape import *
from .medscape_out_date import *
from .LoadJSON import load_json_Medscape
from .forms import *
from .models import *
from .viewsAdd import *

menu = [{'title': "Главная", 'url_name': 'home'},
        {'title': "Добавить данные в БД", 'url_name': 'add_page'},
        ]

add_menu = [{'name_model': "Добавить группу ЛС", 'pk': "1", 'url_name': 'add_DrugGroup'},
            {'name_model': "Добавить ЛС", 'pk': "1", 'url_name': 'add_Drug'},
            ]


def index_views(request):
    ml = ml_model.objects.all()
    context = {
        'ml_model': ml,
        'menu': menu,
        'title': 'Главная страница',
        'ml_model_selected': 0,
        'main_element': 'Главная страница',
    }
    return render(request, 'pharm/index.html', context=context)


def addpage_views(request):
    context = {
        'add_element': add_menu,
        'menu': menu,
        'title': 'Добавить данные в БД',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addElementDB.html', context=context)


def aboutpage_views(request):
    context = {

    }
    return render(request, 'pharm/index.html', context=context)


def addDrugGroup_views(request):
    form = addDrugGroup(request)
    context = {
        'add_element': add_menu,
        'menu': menu,
        'form': form,
        'title': 'Добавить данные в БД',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addDrugGroup.html', context=context)


def addDrug_views(request):
    form = addDrug(request)
    context = {
        'add_element': add_menu,
        'menu': menu,
        'form': form,
        'title': 'Добавить данные в БД',
        'add_element_selected': 0,
    }
    return render(request, 'pharm/addDrugGroup.html', context=context)


def show_model_views(request, ml_model_slug):
    ml = ml_model.objects.all()
    if ml_model_slug == 'test_model':
        context = {
            'ml_model': ml,
            'menu': menu,
            'title': 'Главная страница',
            'main_element': 'show_model + ' + ml_model_slug,
        }
        return render(request, 'pharm/index.html', context=context)
    elif ml_model_slug == 'vyvod-tablichki':
        context = {
            'ml_model': ml,
            'menu': menu,
            'title': 'Главная страница',
            'main_element': 'if show_model + ' + ml_model_slug,
        }
        context.update(all_drug_table(request))
        return render(request, 'pharm/vyvod-tablichki.html', context=context)

    elif ml_model_slug == 'zagruzka-dannyh-iz-medscape':
        s=load_json_Medscape()

        context = {
            'ml_model': ml,
            'menu': menu,
            'title': 'Главная страница',
            'main_element': 'show_model + ' + ml_model_slug+' '+s,
        }
        return render(request, 'pharm/index.html', context=context)
    elif ml_model_slug == 'iteraction_MedScape':

        context = {
            'ml_model': ml,
            'menu': menu,
            'title': 'Главная страница',
            'main_element': 'show_model + ' + ml_model_slug,
        }
        context.update(iteraction_medscape_out(request))
        context.update(iteraction_medscape_two_drugs(request))
        return render(request, 'pharm/iterction_medscape.html', context=context)

    elif ml_model_slug == 'vyvesti-dannye-medscape':


        context = {
            'ml_model': ml,
            'menu': menu,
            'title': 'Главная страница',
            'main_element': 'show_model + ' + ml_model_slug,
        }
        context.update(medscape_out_date(request))
        return render(request, 'pharm/vivod_medscape.html', context=context)
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'pharm/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'pharm/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')
