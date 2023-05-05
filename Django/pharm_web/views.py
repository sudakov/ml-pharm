from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.list import ListView

from .forms import *
from .models import *


def index(request):
    ml = ml_model.objects.all()
    print(ml)
    context = {
        'ml_model': ml,
        'menu': 'menu',
        'title': 'Главная страница',
        'pg_selected': 0,
    }
    return render(request, 'pharm/index.html', context=context)


"""
class PGView(ListView):
    model = ml_model
    template_name = 'pg/index.html'
    context_object_name = 'GraphList'


def index(request):
    pg = ml_model.objects.all()
    context = {
        'pg': pg,
        'menu': menu,
        'title': 'Главная страница',
        'pg_selected': 0,
    }
    PGView.as_view()
    return render(request, 'pg/index.html', context=context)


def about(request):
    return render(request, 'pg/about.html', {'menu': menu, 'title': 'О сайте'})


def addpage(request):
    if request.method == 'POST':
        form = AddPgForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                ParametricGraph.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')

    else:
        form = AddPgForm()
    return render(request, 'pg/addpg.html', {'form': form, 'menu': menu, 'title': 'Добавление параметрического графа'})


def add_layer(request):
    if request.method == 'POST':
        form = AddLayerForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                Layer.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')

    else:
        form = AddLayerForm()
    return render(request, 'pg/addlayer.html', {'form': form, 'menu': menu, 'title': 'Добавление параметра'})


def add_node(request):
    if request.method == 'POST':
        form = AddNodeForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            try:
                Node.objects.create(**form.cleaned_data)
                return redirect('home')
            except:
                form.add_error(None, 'Ошибка добавления поста')

    else:
        form = AddNodeForm()
    return render(request, 'pg/addnode.html', {'form': form, 'menu': menu, 'title': 'Добавление значения'})


def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def show_pg(request, pg_id):
    pg = ParametricGraph.objects.all()
    layer = Layer.objects.filter(pg_id=pg_id)
    node = Node.objects.all()
    #    if len(layer) == 0:
    #       raise Http404()
    print(layer)

    context = {
        'pg': pg,
        'layer': layer,
        'node': node,
        'menu': menu,
        'title': 'Параметрический граф',
        'pg_selected': pg_id,
    }

    return render(request, 'pg/index.html', context=context)


def show_layer(request, layer_id):
    pg = ParametricGraph.objects.all()
    layer = Layer.objects.all()
    print(layer_id)
    node = Node.objects.filter(layer_id=layer_id)
    #    if len(layer) == 0:
    #       raise Http404()
    print(node)

    context = {
        'pg': pg,
        'layer': layer,
        'node': node,
        'menu': menu,
        'title': 'Параметрический граф',
        'pg_selected': 0,
    }

    return render(request, 'pg/indexlayer.html', context=context)

"""


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'pg/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'pg/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')
