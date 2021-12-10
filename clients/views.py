
from django.utils.timezone import now
from datetime import *
from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from clients.forms import ClientForm
from clients.models import Client
from profiles.models import Ciudad, Departamento

def client_create(request):
    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)

    if request.method == "GET":
        context={ "form":form}
        return render(request, template_name, context)

    if request.method == "POST":
        print(form.data)
        if form.is_valid():
            client_obj = form.save(commit=False)
            client_obj.owner = request.user
            client_obj.save()

        return redirect('client_list')

def client_list(request):
    if request.method == "GET":
        client_list = Client.objects.filter(owner = request.user)
        template_name = 'clients/client_list.html'
        context={ "client_list":client_list }

        return render(request, template_name, context)



def client_update(request, *args, **kwargs):
    template_name = 'clients/client_form.html'
    form = ClientForm(request.POST or None)
    client_obj = Client.objects.get(id=kwargs.get('id'))

    if client_obj.owner != request.user:
        return redirect('home')

    if request.method == "GET":
        form = ClientForm(instance=client_obj)
        context={"form":form, "client_obj":client_obj}
        print()
        print(context)
        print()
        return render(request, template_name, context)

    if request.method == "POST":
        form = ClientForm(request.POST)
        print(form.data)
        if form.is_valid():
            client_obj.document = form.data['document']
            client_obj.first_name = form.data['first_name']
            client_obj.last_name = form.data['last_name']
            client_obj.region = Departamento.objects.get(id = form.data['region'])
            client_obj.city = Ciudad.objects.get(id = form.data['city'])
            client_obj.email = form.data['email']
            client_obj.phone1 = form.data['phone1']
            client_obj.phone2 = form.data['phone2']
            client_obj.save()
            

        return redirect('client_list')