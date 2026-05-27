from django.shortcuts import redirect
from django.contrib import messages


class AdminSuperuserOnlyMiddleware:
    """
    Bloqueia acesso ao painel Django Admin (/admin/) para utilizadores
    que não sejam superutilizadores.
    Redireciona para o dashboard com uma mensagem de aviso.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            if user.is_authenticated and not user.is_superuser:
                messages.warning(
                    request,
                    'Não tem permissão para aceder ao painel de administração.'
                )
                return redirect('dashboard')
        return self.get_response(request)
