from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User
from .models import Cliente, Perfil
from .forms import ClienteForm, UserProfileForm

@login_required
def perfil_edit(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            perfil.telefone = form.cleaned_data.get('telefone')
            perfil.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user, initial={'telefone': perfil.telefone})
    
    return render(request, 'clientes/perfil_form.html', {'form': form})

@login_required
def cliente_list(request):
    search_query = request.GET.get('q') or request.GET.get('search', '')
    if search_query:
        clientes = Cliente.objects.filter(models.Q(nome__icontains=search_query) | models.Q(numero_cliente__icontains=search_query))
    else:
        clientes = Cliente.objects.all()
    return render(request, 'clientes/cliente_list.html', {'clientes': clientes, 'search_query': search_query})

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado com sucesso!")
            return redirect('cliente_list')
        else:
            messages.error(request, "Erro ao registrar cliente. Verifique os dados.")
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form, 'title': 'Registrar Cliente'})

@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados do cliente atualizados!")
            return redirect('cliente_list')
        else:
            messages.error(request, "Erro ao atualizar dados. Verifique o formulário.")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'title': 'Editar Cliente'})

@login_required
def cliente_toggle_status(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.status = 'INATIVO' if cliente.status == 'ATIVO' else 'ATIVO'
    cliente.save()
    messages.info(request, f"Status do cliente {cliente.nome} alterado para {cliente.status}.")
    return redirect('cliente_list')
