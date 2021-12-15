
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from clients.forms import ClientForm
from clients.models import Client
from profiles.models import Ciudad, Departamento, Profile

@login_required()
def client_create(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile
    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)

    if request.method == "GET":
        context['form'] = form
        return render(request, template_name, context)

    if request.method == "POST":
        print(form.data)
        if form.is_valid():
            client_obj = form.save(commit=False)
            client_obj.owner = request.user
            client_obj.company = profile.company
            client_obj.save()

        return redirect('client_list')

@login_required()
def client_list(request):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile
    if request.method == "GET":
        client_list = Client.objects.filter(company = profile.company)
        template_name = 'clients/client_list.html'
        context['client_list'] = client_list

        return render(request, template_name, context)

@login_required()
def client_update(request, *args, **kwargs):
    try:
        profile = Profile.objects.get(user = request.user, active = True)
    except:
        return redirect('blank')

    context = {}
    context['profile'] = profile

    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)
    client_obj = Client.objects.get(id=kwargs.get('id'))

    if client_obj.company != profile.company:
        return redirect('home')

    if request.method == "GET":
        form = ClientForm(instance=client_obj)
        context['form'] = form
        context['client_obj'] = client_obj
        print()
        print(context)
        print()
        return render(request, template_name, context)

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client_obj.document = form.data['document']
            client_obj.first_name = form.data['first_name']
            client_obj.last_name = form.data['last_name']
            client_obj.region = Departamento.objects.get(id = form.data['region'])
            client_obj.city = Ciudad.objects.get(id = form.data['city'])
            client_obj.email = form.data['email']
            client_obj.phone1 = form.data['phone1']
            client_obj.phone2 = form.data['phone2']
            try:
                visibility = request.POST['visibility']
                client_obj.visibility = True
            except:
                client_obj.visibility = False
            
            client_obj.save()
            

        return redirect('client_list')