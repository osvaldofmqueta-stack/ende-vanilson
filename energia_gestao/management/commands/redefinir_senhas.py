from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clientes.models import Perfil

UTILIZADORES = [
    {'username': 'admin',      'password': 'admin@2025', 'email': 'admin@energia.ao',  'tipo': 'ADMIN',      'is_staff': True,  'is_superuser': True},
    {'username': 'financeiro', 'password': 'fin@2025',   'email': 'fin@energia.ao',    'tipo': 'FINANCEIRO', 'is_staff': False, 'is_superuser': False},
    {'username': 'operador',   'password': 'oper@2025',  'email': 'oper@energia.ao',   'tipo': 'OPERADOR',   'is_staff': False, 'is_superuser': False},
]


class Command(BaseCommand):
    help = 'Redefine as senhas dos utilizadores padrao para os valores originais'

    def handle(self, *args, **options):
        self.stdout.write('\n  A redefinir senhas dos utilizadores padrao...\n')
        for u in UTILIZADORES:
            user, created = User.objects.get_or_create(username=u['username'])
            user.set_password(u['password'])
            user.email = u['email']
            user.is_staff = u['is_staff']
            user.is_superuser = u['is_superuser']
            user.save()
            Perfil.objects.get_or_create(user=user, defaults={'tipo_usuario': u['tipo']})
            estado = 'criado' if created else 'atualizado'
            self.stdout.write(self.style.SUCCESS(f'  OK  {u["username"]} ({estado}) -> senha: {u["password"]}'))

        self.stdout.write(self.style.SUCCESS('\n  Senhas redefinidas com sucesso!\n'))
