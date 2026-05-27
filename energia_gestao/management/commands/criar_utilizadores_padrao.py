from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clientes.models import Perfil


UTILIZADORES = [
    {'username': 'admin',      'password': 'admin@2025', 'email': 'admin@energia.ao',  'tipo': 'ADMIN',      'is_staff': True,  'is_superuser': True},
    {'username': 'financeiro', 'password': 'fin@2025',   'email': 'fin@energia.ao',    'tipo': 'FINANCEIRO', 'is_staff': False, 'is_superuser': False},
    {'username': 'operador',   'password': 'oper@2025',  'email': 'oper@energia.ao',   'tipo': 'OPERADOR',   'is_staff': False, 'is_superuser': False},
]


class Command(BaseCommand):
    help = 'Cria utilizadores padrão caso não existam'

    def handle(self, *args, **options):
        criados = 0
        for u in UTILIZADORES:
            if not User.objects.filter(username=u['username']).exists():
                user = User.objects.create_user(
                    username=u['username'],
                    password=u['password'],
                    email=u['email'],
                    is_staff=u['is_staff'],
                    is_superuser=u['is_superuser'],
                )
                Perfil.objects.get_or_create(user=user, defaults={'tipo_usuario': u['tipo']})
                criados += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Criado: {u['username']}"))
            else:
                self.stdout.write(f"  → Já existe: {u['username']}")

        self.stdout.write(self.style.SUCCESS(f"\nConcluído — {criados} utilizador(es) criado(s)."))
