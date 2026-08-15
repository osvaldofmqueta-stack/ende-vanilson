from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Compatibilidade: cria utilizadores sem redefinir passwords existentes'

    def handle(self, *args, **options):
        self.stdout.write(
            'Este comando foi mantido por compatibilidade. '
            'As passwords existentes nao serao alteradas.\n'
        )
        call_command('criar_utilizadores_padrao')
