"""Compatibilidade para instalações antigas.

Use `python manage.py criar_utilizadores_padrao` para criar utilizadores.
Durante uma instalação automática, use `--auto-passwords` e
`--credentials-file` para gerar e guardar as credenciais localmente.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energia_gestao.settings')

import django

django.setup()

from django.core.management import call_command


call_command('criar_utilizadores_padrao')
