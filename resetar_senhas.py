"""
Script para redefinir as senhas dos utilizadores padrao.
Execute com: python resetar_senhas.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energia_gestao.settings')
django.setup()

from django.contrib.auth.models import User
from clientes.models import Perfil

UTILIZADORES = [
    {'username': 'admin',      'password': 'admin@2025', 'email': 'admin@energia.ao',  'tipo': 'ADMIN',      'is_staff': True,  'is_superuser': True},
    {'username': 'financeiro', 'password': 'fin@2025',   'email': 'fin@energia.ao',    'tipo': 'FINANCEIRO', 'is_staff': False, 'is_superuser': False},
    {'username': 'operador',   'password': 'oper@2025',  'email': 'oper@energia.ao',   'tipo': 'OPERADOR',   'is_staff': False, 'is_superuser': False},
]

print()
print('  ============================================================')
print('    REDEFINICAO DE SENHAS - SISTEMA DE GESTAO DE ENERGIA')
print('  ============================================================')
print()

for u in UTILIZADORES:
    user, created = User.objects.get_or_create(username=u['username'])
    user.set_password(u['password'])
    user.email = u['email']
    user.is_staff = u['is_staff']
    user.is_superuser = u['is_superuser']
    user.save()
    Perfil.objects.get_or_create(user=user, defaults={'tipo_usuario': u['tipo']})
    estado = 'CRIADO' if created else 'ATUALIZADO'
    print(f'  [{estado}]  {u["username"]}  ->  senha: {u["password"]}')

print()
print('  Senhas redefinidas com sucesso!')
print()
print('  Credenciais de acesso:')
print('  ----------------------------------------------------------')
print('   Administrador :  admin       /  admin@2025')
print('   Financeiro    :  financeiro  /  fin@2025')
print('   Operador      :  operador    /  oper@2025')
print('  ----------------------------------------------------------')
print()
