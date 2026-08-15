import getpass
import os
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from clientes.models import Perfil


UTILIZADORES = [
    {'username': 'admin', 'email': 'admin@energia.ao', 'tipo': 'ADMIN', 'is_staff': True, 'is_superuser': True},
    {'username': 'financeiro', 'email': 'fin@energia.ao', 'tipo': 'FINANCEIRO', 'is_staff': False, 'is_superuser': False},
    {'username': 'operador', 'email': 'oper@energia.ao', 'tipo': 'OPERADOR', 'is_staff': False, 'is_superuser': False},
]


class Command(BaseCommand):
    help = 'Cria utilizadores padrão sem definir palavras-passe públicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-existing',
            action='store_true',
            help='Atualiza também as passwords dos utilizadores existentes',
        )
        parser.add_argument(
            '--credentials-file',
            help='Ficheiro temporário onde será escrito o resumo das credenciais',
        )

    def handle(self, *args, **options):
        criados = 0
        atualizados = 0
        credenciais = []
        for utilizador in UTILIZADORES:
            user = User.objects.filter(username=utilizador['username']).first()
            if user and not options['reset_existing']:
                Perfil.objects.get_or_create(
                    user=user,
                    defaults={'tipo_usuario': utilizador['tipo']},
                )
                self.stdout.write(
                    f"  -> Ja existe: {utilizador['username']} (password mantida)"
                )
                credenciais.append(
                    (utilizador['username'], '[password existente — não alterada]')
                )
                continue

            password = self._get_password(utilizador['username'])
            if user:
                user.set_password(password)
                user.email = utilizador['email']
                user.is_staff = utilizador['is_staff']
                user.is_superuser = utilizador['is_superuser']
                user.save()
                atualizados += 1
                estado = 'Atualizado'
            else:
                user = User.objects.create_user(
                    username=utilizador['username'],
                    password=password,
                    email=utilizador['email'],
                    is_staff=utilizador['is_staff'],
                    is_superuser=utilizador['is_superuser'],
                )
                criados += 1
                estado = 'Criado'

            Perfil.objects.get_or_create(
                user=user,
                defaults={'tipo_usuario': utilizador['tipo']},
            )
            self.stdout.write(
                self.style.SUCCESS(f"  OK  {estado}: {utilizador['username']}")
            )
            credenciais.append((utilizador['username'], password))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído — {criados} criado(s), {atualizados} atualizado(s)."
            )
        )
        if options['credentials_file']:
            self._write_credentials_file(options['credentials_file'], credenciais)

    def _get_password(self, username):
        env_name = f"{username.upper()}_PASSWORD"
        password = os.environ.get(env_name)
        if password:
            return password

        if not os.isatty(0):
            raise CommandError(
                f"Defina {env_name} no ambiente ou execute este comando num "
                "terminal para definir a password de forma interativa."
            )

        while True:
            password = getpass.getpass(
                f"Password para {username} (minimo 8 caracteres): "
            )
            confirmation = getpass.getpass("Confirme a password: ")
            if len(password) < 8:
                self.stderr.write("A password deve ter pelo menos 8 caracteres.")
            elif password != confirmation:
                self.stderr.write("As passwords nao coincidem.")
            else:
                return password

    def _write_credentials_file(self, filename, credentials):
        try:
            path = Path(filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            lines = [
                '',
                '  CREDENCIAIS DE ACESSO DESTA INSTALACAO',
                '  ----------------------------------------------------------',
            ]
            for username, password in credentials:
                lines.append(f'   {username:<14} /  {password}')
            lines.extend([
                '  ----------------------------------------------------------',
                '  Guarde estas credenciais num local seguro.',
                '',
            ])
            path.write_text('\n'.join(lines), encoding='utf-8')
        except OSError as exc:
            raise CommandError(
                f'Nao foi possivel preparar o resumo das credenciais: {exc}'
            ) from exc
